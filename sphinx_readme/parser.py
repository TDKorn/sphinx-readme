import re
from pathlib import Path
from collections import defaultdict
from functools import cached_property
from typing import Dict, List, Set, Union, Callable, Optional, Tuple, Iterable

from docutils import nodes
from sphinx import addnodes
from sphinx.domains.python import ObjectEntry
from sphinx.application import Sphinx, BuildEnvironment

from sphinx_readme.config import READMEConfig
from sphinx_readme.utils.docutils import get_doctree, parse_node_text
from sphinx_readme.utils.sphinx import get_conf_val, ExternalRef
from sphinx_readme.utils.rst import get_all_xref_variants, escape_rst, format_rst, replace_xrefs, format_hyperlink, BEFORE_XREF, AFTER_XREF


class READMEParser:

    def __init__(self, app: Sphinx):
        #: The :class:`~.READMEConfig` for the parser
        self.config: READMEConfig = READMEConfig(app)
        self.logger = self.config.logger
        #: Mapping of info for standard and :mod:`sphinx.ext.autodoc` cross-references
        self.ref_map: Dict[str, Union[List, Dict]] = {}
        #: Mapping of source files to their content
        self.sources: Dict[str, str] = self.config.sources
        #: Mapping of source files to their toctree data
        self.toctrees: Dict[str, List[Dict]] = defaultdict(list)
        #: Mapping of source files to their admonition data
        self.admonitions: Dict[str, List[Dict]] = {}
        #: Mapping of source files to their rubric data
        self.rubrics: Dict[str, List[str]] = {}
        #: Mapping of source files to cross-reference substitution definitions
        self.substitutions: Dict[str, Dict[str, List[str]]] = defaultdict(dict)
        #: Mapping of docnames to their parsed titles
        self.titles: Dict[str, str] = {}
        #: Tuple of currently supported Sphinx domains
        self.domains: Tuple = ("py", "std", "rst")
        #: Mapping of domain names to their cross-reference roles
        self.roles: Dict[str, List[str]] = {}
        #: Mapping of role names to the object types they can cross-reference
        self.objtypes: Dict[str, List[str]] = {}
        #: Packages in the intersphinx cache
        self.intersphinx_pkgs: List[str] = []
        #: Easy access to intersphinx inventory
        self.inventory: Dict[str, Dict] = {}
        #: Easy access to intersphinx named inventory
        self.named_inventory: Dict[str, Dict] = {}

    def parse_env(self, env: BuildEnvironment) -> None:
        """Parses domain data and document titles from the |env|"""
        self.parse_titles(env)
        self.parse_roles(env)
        self.parse_objtypes(env)
        self.parse_py_domain(env)
        self.parse_std_domain(env)

        # Add access to data from intersphinx, if applicable
        self.inventory = getattr(env, 'intersphinx_inventory', {})
        self.named_inventory = getattr(env, 'intersphinx_named_inventory', {})
        self.intersphinx_pkgs = list(getattr(env, 'intersphinx_named_inventory', {}))

    def parse_titles(self, env: BuildEnvironment) -> None:
        """Parses document and section titles from the |env|"""
        for docname in env.found_docs:
            doctree = env.get_doctree(docname)
            sections = list(doctree.findall(nodes.section))

            for section in sections:
                # Parse titles of sections referenced with :ref:
                if getattr(section, "expect_referenced_by_name", None):
                    ref_id = list(section.expect_referenced_by_name)[0]
                    title = section.next_node(nodes.title).rawsource
                    self.titles[ref_id] = replace_xrefs(title)

            try:
                # Parse title of document for :doc: refs
                h1 = sections[0].next_node(nodes.title).rawsource
                self.titles[docname] = replace_xrefs(h1)

            except IndexError:
                continue  # Document without title

    def parse_roles(self, env: BuildEnvironment) -> None:
        """Parses the available roles for cross-referencing objects in the
        |py_domain|, |std_domain|, and |rst_domain|

        :param env: the |env|
        """
        for domain in self.domains:
            self.roles[domain] = list(env.get_domain(domain).roles)

    def parse_objtypes(self, env: BuildEnvironment) -> None:
        """Maps cross-reference roles to their corresponding object types in the
        |py_domain|, |std_domain|, and |rst_domain|

        :param env: the |env|
        """
        for domain in self.domains:
            for role in self.roles[domain]:
                self.objtypes[role] = [
                    f"{domain}:{objtype}"  # Prefix with domain to match intersphinx inventory
                    for objtype in env.get_domain(domain).objtypes_for_role(role, [])
                ]

    def parse_std_domain(self, env: BuildEnvironment) -> None:
        """Parses cross-reference data from the |std_domain|

        :param env: the |env|
        """
        for ref_id, text, role, docname, anchor, _ in env.get_domain("std").get_objects():
            replace = self.titles.get(ref_id) or text
            target = f"{self.config.html_baseurl}/{docname}.html"

            if anchor:
                target += f"#{anchor}"

            if role == "confval" and self.config.inline_markup:
                replace = f"``{replace}``"

            elif role == "label":
                role = "ref"

            self.ref_map.setdefault(role, {})[ref_id] = {
                "replace": replace,
                "target": target
            }

    def parse_py_domain(self, env: BuildEnvironment) -> None:
        """Parses cross-reference data for |py_domain| objects

        :param env: the |env|
        """
        py_objects = env.domaindata.get('py', {}).get("objects", {})
        linkcode_resolve = get_conf_val(env, "linkcode_resolve")

        for qualname, entry in py_objects.items():
            if target := self.get_py_target(entry, linkcode_resolve):
                self.add_variants(
                    qualified_name=qualname,
                    target=target,
                    is_callable=entry.objtype in ("method", "function"))

    def get_py_target(self, entry: ObjectEntry, linkcode_resolve: Optional[Callable] = None) -> Optional[str]:
        """Resolves the target for a cross-reference to an object in the |py_domain|

        :param entry: the ``ObjectEntry`` for the object
        :param linkcode_resolve: function to resolve targets when linking to source code
        :return: the link to the object's corresponding documentation entry or highlighted source code
        """
        if self.config.docs_url_type == "html":
            # All links to html documentation follow the same format
            return f"{self.config.html_baseurl}/{entry.docname}.html#{entry.node_id}"

        if entry.objtype in ("attribute", "data"):
            return None  # Cannot link to source code

        # Use linkcode_resolve to generate links
        info = dict.fromkeys(("module", "fullname"))
        parts = entry.node_id.removeprefix('module-').split('.')

        if entry.objtype in ("class", "function", "module", "exception"):
            info["module"] = '.'.join(parts[:-1])
            info['fullname'] = parts[-1]

        elif entry.objtype in ("method", "property"):
            info["module"] = '.'.join(parts[:-2])
            info['fullname'] = '.'.join(parts[-2:])

        link = linkcode_resolve("py", info)

        if link and entry.objtype == 'module':
            link = link.split('#')[0]  # Avoid highlighting whole file

        return link

    def add_variants(self, qualified_name: str, target: str, is_callable: bool = False) -> None:
        """Adds substitution information for an object to the :attr:`ref_map`

        This data is used to replace any :mod:`~sphinx.ext.autodoc` cross-reference to
        the object with a substitution, hyperlinked to the corresponding
        source code or documentation entry

        .. tip:: See :func:`~.get_all_xref_variants` and :meth:`replace_autodoc_refs`

        :param qualified_name: the fully qualified name of an object (ex. ``"sphinx_readme.parser.add_variants"``)
        :param target: the refuri of the object's corresponding source code or documentation entry
        :param is_callable: specifies if the object is a method or function
        """
        short_ref = qualified_name.split('.')[-1]
        variants = get_all_xref_variants(qualified_name)

        for variant in variants:
            if variant in self.ref_map:
                continue

            if variant.startswith("~"):
                replace = short_ref
            else:
                replace = variant.lstrip('.')

            if is_callable:
                replace += "()"

            if self.config.inline_markup:
                replace = f"``{replace}``"

            self.ref_map[variant] = {
                'replace': replace,
                'target': target
            }

    def parse_doctree(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        """Parses cross-reference, admonition, rubric, and toctree data from a resolved doctree"""
        if doctree.get('source') in self.sources:
            self.parse_admonitions(app, doctree, docname)
            self.parse_rubrics(app, doctree, docname)
            self.parse_toctrees(app, doctree, docname)
            self.parse_intersphinx_nodes(app, doctree, docname)

    def parse_admonitions(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        """Parses data from generic and specific admonitions

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        src = doctree.get('source')
        rst = self.sources[src]
        admonitions = []

        # Generate new doctree to account for only directives
        doctree = get_doctree(app, rst, docname)

        for admonition in list(doctree.findall(nodes.Admonition)):
            info = {
                'body': admonition.rawsource
            }
            if isinstance(admonition, nodes.admonition):
                # Generic Admonition (using admonition directive)
                info.update({
                    'type': 'generic',
                    'class': admonition.get('classes')[0],
                    'title': admonition.children[0].rawsource
                })
            else:
                # Specific Admonition (for example, .. note::)
                info.update({
                    'type': 'specific',
                    'class': admonition.tagname,
                    'title': admonition.tagname.title()
                })
            admonitions.append(info)

        self.admonitions[src] = admonitions

    def parse_intersphinx_nodes(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        """Parses cross-references that utilize :mod:`sphinx.ext.intersphinx`

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        xref_pattern, xref_title_pattern = self.get_xref_regex(self.domains, roles=self.objtypes.keys())
        src = doctree.get('source')
        rst = self.sources[src]
        nodes_to_parse = []

        reference_nodes = list(doctree.findall(nodes.reference))

        # Add reference nodes from substitutions
        for sub in doctree.substitution_defs.values():
            if isinstance(sub.children[0], nodes.reference):
                reference_nodes.append(sub.children[0])

        # Keep nodes with external URIs
        for node in reference_nodes:
            if node.get('internal') is False:
                nodes_to_parse.append(node.children[0])

        # Generate new doctree to account for only directives, then add problematic nodes
        problematic_nodes = get_doctree(app, rst, docname).findall(nodes.problematic)
        nodes_to_parse.extend(problematic_nodes)

        # Parse xrefs from nodes
        for node in nodes_to_parse:
            if '<' in node.rawsource:
                pattern = xref_title_pattern
            else:
                pattern = xref_pattern

            if not (match := re.match(pattern, node.rawsource)):
                continue

            _, external, role, *_, ref_id = match.groups()
            self.parse_external_node(external, role, ref_id.lstrip('~.'))

    def parse_external_node(self, external, role, ref_id) -> None:
        objtypes = self.objtypes[role]

        for objtype in objtypes:  # Check intersphinx inventory for applicable objtypes
            if xref := self.get_external_ref(external, objtype, ref_id):
                break

        if xref is None:
            return

        if xref.objtype.startswith("py"):
            is_callable = xref.objtype in ("py:method", "py:function")
            self.add_variants(xref.id, xref.target, is_callable)

        else:
            if self.config.inline_markup and xref.objtype not in ('std:label', 'std:doc'):
                xref.label = f"``{xref.label}``"

            self.ref_map.setdefault(role, {}).setdefault(xref.id, {
                "replace": xref.label,
                "target": xref.target
            })

    def parse_toctrees(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        """Parses the caption and entry data from :class:`~.sphinx.addnodes.toctree` nodes

        .. caution:: Toctrees are currently parsed as if the directive has the ``:titlesonly:`` option

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        source = doctree.get('source')
        tocs = app.env.tocs

        for toctree in list(doctree.findall(addnodes.toctree)):
            toc = self._parse_toctree(toctree, docname, tocs)
            self.toctrees[source].append(toc)

    def _parse_toctree(self, toctree, docname, tocs, is_subtoc=False):
        toc = {
            'caption': toctree.get('caption'),
            'titles_only': toctree.get('titlesonly'),
            'entries': []
        }
        if toctree.get('maxdepth') != 1:
            toc['maxdepth'] = toctree.get('maxdepth')

        for text, entry in toctree.get('entries', []):
            entry = entry if entry != 'self' else docname
            title = text if text else self.titles.get(entry)
            subtree = tocs[entry].next_node(nodes.bullet_list)

            if subtree:
                if is_subtoc or 'maxdepth' in toc:
                    subtree = self._parse_subtree(subtree, tocs)

            toc['entries'].append({
                'entry': entry,
                'title': title,
                'entries': subtree
            })
        return toc

    def _parse_subtree(self, tree: nodes.bullet_list, tocs: Dict[str, nodes.bullet_list]) -> List[Dict]:
        sub_trees = []

        for child in tree.children:
            if isinstance(child, addnodes.toctree):
                sub_toc = self._parse_toctree(
                    docname=Path(child.source).stem,
                    is_subtoc=True, tocs=tocs,
                    toctree=child,
                )
                for entry in sub_toc['entries']:
                    entry['is_subtoc'] = True

                sub_trees.extend(sub_toc['entries'])
                continue

            if not isinstance(child, nodes.list_item):
                continue

            sub_tree = {
                'entry': None,
                'anchor': None,
                'title': None,
                'entries': []
            }
            for item in child.children:
                if isinstance(item, addnodes.compact_paragraph):
                    ref_node = child.next_node(nodes.reference)
                    sub_tree['title'] = parse_node_text(ref_node)
                    sub_tree['anchor'] = ref_node.get('anchorname')
                    sub_tree['entry'] = ref_node.get('refuri')

                elif isinstance(item, nodes.bullet_list):
                    sub_tree['entries'].extend(self._parse_subtree(item, tocs))

            sub_trees.append(sub_tree)
        return sub_trees

    def parse_rubrics(self, app: Sphinx, doctree: nodes.document, docname: str) -> None:
        """Parses the content from :rst:dir:`rubric` directives"""
        source = doctree.get('source')
        rst = self.sources[source]
        rubrics = []

        # Generate new doctree to account for only directives
        doctree = get_doctree(app, rst, docname)

        for rubric in doctree.findall(nodes.rubric):
            rubrics.append(rubric.rawsource)

        self.rubrics[source] = rubrics

    def get_external_ref(self, external: str, objtype: str, ref_id: str) -> Optional[ExternalRef]:
        """Retrieves external cross-reference data from the :mod:`sphinx.ext.intersphinx` inventory

        :param external: the ``:external:`` or ``:external+pkg:`` portion of the xref, if present
        :param objtype: the name of the object type being referenced
        :param ref_id: the target of the cross-reference
        :return: an :class:`~.ExternalRef` object if the lookup was successful, otherwise ``None``
        """
        pkg = None  # First, attempt to constrain lookup to specific package

        # Check for :external+pkg:role:`ref_id` syntax
        if external and "+" in external:
            pkg = external.split('+')[-1]

        # Check for :role:`pkg:ref_id` syntax
        elif ":" in ref_id:
            tokens = ref_id.split(":", maxsplit=1)

            # Ensure it's not `directive:option` or `doc:section`
            if tokens[0] in self.intersphinx_pkgs:
                pkg, ref_id = tokens

        if objtype == "std:label":
            ref_id = nodes.fully_normalize_name(ref_id)

        # Lookup reference in intersphinx named or regular inventory
        inventory = self.named_inventory.get(pkg, self.inventory)

        if xref := inventory.get(objtype, {}).get(ref_id):
            return ExternalRef(objtype, *xref, ref_id)

    def get_external_id(self, external: str, role: str, ref_id: str) -> Optional[str]:
        """Helper function to get the ``ref_id`` when replacing external xrefs"""
        for objtype in self.objtypes[role]:
            if xref := self.get_external_ref(external, objtype, ref_id):
                return xref.id

    def is_external_xref(self, external: str, role: str, ref_id: str) -> bool:
        """Helper function to check if a cross-reference is explicitly external"""
        return any((
            external,
            role in self.roles['rst'],
            ":" in ref_id and ref_id.split(":", maxsplit=1)[0] in self.intersphinx_pkgs
        ))

    def resolve(self) -> None:
        """Uses parsed data from to replace cross-references and directives in the :attr:`~.src_files`

        Once resolved, files are written to the :attr:`~.out_dir`.
        """
        for src, rst in self.sources.items():
            # Replace everything using parsed data
            rst = self.replace_admonitions(src, rst)
            rst = self.replace_rst_images(src, rst)
            rst = self.replace_toctrees(src, rst)
            rst = self.replace_rubrics(src, rst)
            rst = self.replace_xrefs(src, rst)
            rst = self.replace_py_xrefs(src, rst)
            rst = self.replace_unresolved_xrefs(rst)

            # Prepend substitution definitions for cross-reference
            substitutions = self.substitutions[src]
            header_vals = []

            for target in sorted(substitutions, key=lambda t: (t.lower().lstrip("`~."), t.lower())):
                header_vals.append('\n'.join(substitutions[target]))

            # Write the final output
            rst_out = self.config.src_files[src]
            rst_out.parent.mkdir(parents=True, exist_ok=True)

            output = "\n".join(header_vals) + "\n\n" + rst
            rst_out.write_text(output, encoding='utf-8')

            print(f'``sphinx_readme``: saved generated file to {rst_out}')

    def replace_admonitions(self, rst_src: str, rst: str) -> str:
        """Replaces generic and specific admonition directives with HTML tables or ``list-table``
        directives, depending on the value of :confval:`readme_raw_directive`

        .. admonition:: Customizing Admonitions
           :class: about

           The :attr:`~.icon_map` can be overriden to use custom admonition icons/classes

           * See :confval:`readme_admonition_icons` and :confval:`readme_default_admonition_icon`

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        for admonition in self.admonitions[rst_src]:
            if not (pattern := self.get_admonition_regex(admonition)):
                continue

            icon = self.get_admonition_icon(admonition)
            if not self.config.raw_directive:
                rst = re.sub(
                    pattern=pattern,
                    repl=lambda match: self._replace_admonition(
                        match, rst_src, admonition, icon),
                    string=rst,
                )
            else:
                rst = re.sub(
                    pattern=pattern,
                    repl=self.config.admonition_template.format(
                        title=admonition['title'],
                        text=admonition['body'],
                        icon=icon),
                    string=rst
                )
        return rst

    def _replace_admonition(self, match, rst_src, admonition: dict, icon: str) -> str:
        """Helper function for formatting ``list-table`` admonitions"""
        body = match.group(2)
        if all((
                ".. rubric::" in body,
                self.config.rubric_heading,
                self.config.raw_directive is False
        )):
            body = self.replace_rubrics(rst_src, body, force_markup=True)

        # Add extra indentation to ensure body lines up with directive
        body = re.sub(pattern=r"(\n+)", repl=r"\1    ", string=body)
        template = self.config.admonition_template.format(
            title=admonition['title'],
            icon=icon
        ).replace(
            r'\2', body
        ).replace(
            r'\1', match.group(1)
        )
        return template

    def replace_toctrees(self, rst_src: str, rst: str) -> str:
        """Replaces :rst:dir:`toctree` directives with hyperlinked bullet lists

        .. note:: Entries will link to HTML documentation regardless of the
           value of :confval:`readme_docs_url_type`

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        pattern = r"\.\. toctree::\s*?\n+?(?:^[ ]+.+?$|^\s*$)+?(?=\n*\S+|\Z)"
        toctrees = re.findall(pattern, rst, re.M | re.DOTALL)

        for toctree, info in zip(toctrees, self.toctrees[rst_src]):
            titles_only = info.get('titles_only')
            maxdepth = info.get('maxdepth', 1)
            repl = ""

            if info['caption']:
                repl += f"**{info['caption']}**\n\n"

            for entry in info['entries']:
                repl = self._replace_toctree_entry(rst_src, entry, repl, maxdepth, titles_only)

            last_line = repl.strip().split('\n')[-1]
            last_indent = len(last_line) - len(last_line.lstrip())
            repl += f"\n{(last_indent + 2) * ' '}|\n\n"  # Add line break at next indent to improve spacing

            # Replace toctree directive with substitutions
            rst = rst.replace(toctree, repl)

        return rst

    def _replace_toctree_entry(self, rst_src, entry, repl, maxdepth, titles_only, indentation = "", depth = 0):
        if depth == maxdepth:
            return repl

        if depth == 1 and titles_only:
            if not entry.get('is_subtoc'):
                return repl

        # Replace each entry with a link to html docs
        target = f"{self.config.html_baseurl}/{entry['entry']}.html{entry.get('anchor', '')}"
        link, subs = format_hyperlink(target, text=entry['title'])
        repl += f"{indentation}* {link}\n"

        if subs:
            ref_id = entry['title'].replace("`", "")
            self.substitutions[rst_src][ref_id] = subs

        if entry['entries']:
            repl += "\n"  # Add new line for new level
            for sub_entry in entry["entries"]:
                repl = self._replace_toctree_entry(
                    rst_src, sub_entry, repl, maxdepth, titles_only,
                    indentation=f"{indentation}  ",
                    depth=depth + 1
                )
            repl += "\n"
        return repl

    def replace_rst_images(self, rst_src: str, rst: str) -> str:
        """Replaces filepaths in ``image`` directives with repository links

        **Example:**

            :rst:`.. image:: /_static/logo_readme.png`

            would be replaced with

            :rst:`.. image:: https://raw.githubusercontent.com/tdkorn/sphinx-readme/main/docs/source/_static/logo_readme.png`

        .. note:: Your repository will be used as the image source regardless of the
           value of :confval:`readme_docs_url_type`

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        src_dir = self.config.src_dir
        repo_dir = self.config.repo_dir
        rst_src_dir = Path(rst_src).parent
        relpath_to_src_dir = src_dir.relative_to(repo_dir)

        # Find the targets of all image directives
        img_pattern = r"\.\. image:: ([./\w-]+\.\w{3,4})"
        img_paths = re.findall(img_pattern, rst)

        for img_path in img_paths:
            if img_path.startswith("/"):
                # These paths are relative to source dir
                path_to_img = Path(f"{relpath_to_src_dir}{img_path}").as_posix()

            else:
                # These paths are relative to rst_file dir
                abs_img_path = (rst_src_dir / Path(img_path)).resolve()

                # Find path of image relative to the repo directory
                path_to_img = abs_img_path.relative_to(repo_dir).as_posix()

            # Sub that hoe in!!!
            rst = re.sub(
                pattern=rf"\.\. image:: {img_path}",
                repl=fr".. image:: {self.config.image_baseurl}/{path_to_img}",
                string=rst
            )
        return rst

    def replace_rubrics(self, rst_src: str, rst: str, force_markup: bool = False) -> str:
        """Replaces :rst:dir:`rubric` directives with the section heading
        character specified by :confval:`readme_rubric_heading`

        If :confval:`readme_rubric_heading` is not specified, the rubric
        will be replaced with bold text instead

        ...

        **Example:**

        Consider a source file that contains
        :rst:`.. rubric:: This is a \`\`rubric\`\` directive`

        * Replacement without specifying ``readme_rubric_heading``::

              **This is a** ``rubric`` **directive**

        * Replacement if :code:`readme_rubric_heading = "^"`::

              This is a ``rubric`` directive
              ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        rubric_pattern = r'\.\. rubric:: ({body})(?=\n?$(?:\n+?^\s*$|\Z))'
        heading_chars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'

        if heading := self.config.rubric_heading:
            if heading not in heading_chars:
                heading = None

        for rubric in self.rubrics[rst_src]:
            pattern = rubric_pattern.format(body=re.escape(rubric).replace("\\\n", "\\\n[ ]+"))
            text = ' '.join(line.strip() for line in rubric.split('\n'))

            if heading and not force_markup:
                repl = text + "\n" + (len(text) * heading)
            else:
                text = self.replace_xrefs(rst_src, text)
                text = self.replace_py_xrefs(rst_src, text)
                repl = format_rst("bold", text)

            repl = repl.replace("\\", r"\\")
            rst = re.sub(pattern, repl, rst, flags=re.M)

        return rst

    def replace_xrefs(self, rst_src: str, rst: str) -> str:
        """Replaces cross-references from the |std_domain| and |rst_domain| with substitutions or inline links

        .. tip:: This includes cross-references for any custom objects added by
           :meth:`Sphinx.add_object_type() <sphinx.application.Sphinx.add_object_type>`

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        :return: the ``rst`` with all applicable cross-references replaced by links/substitutions
        """
        xrefs = set()

        for pattern in self.get_xref_regex(domains=["rst", "std"]):
            xrefs.update(re.findall(
                pattern=pattern,
                string=rst))

        for xref in xrefs:
            if len(xref) == 5:  # From title pattern
                full_xref, external, role, title, ref_id = xref
            else:
                full_xref, external, role, ref_id, *title = xref

            # If xref is explicitly external, force resolve with external lookup
            if is_explicitly_external := self.is_external_xref(external, role, ref_id):
                ref_id = self.get_external_id(external, role, ref_id)

            elif role == "ref":  # Normalize ref_id to ensure match in ref_map
                ref_id = nodes.fully_normalize_name(ref_id)

            elif role == "doc":
                if ref_id.startswith("/"):
                    # These document paths are relative to source dir
                    ref_id = ref_id.lstrip('/')
                else:
                    # These document paths are relative to rst_src dir
                    abs_doc_path = (Path(rst_src).parent/Path(ref_id)).resolve()
                    ref_id = abs_doc_path.relative_to(self.config.src_dir).as_posix()

            # Match the xref with target data in the ref_map
            ref_map = self.ref_map.get(role, {})

            if ref_id not in ref_map and not is_explicitly_external:
                # If data is missing and the xref isn't explicitly external, check
                # intersphinx since it's also used as a fallback resolution
                ref_id = self.get_external_id(external, role, ref_id)

            if not (info := ref_map.get(ref_id)):
                continue

            if title:  # Include explicit title in substitution name
                ref_id = f"{ref_id}+{title}"

                # Add inline markup if replacement had it
                if info['replace'].startswith("`"):
                    title = f"``{title}``"

            link, subs = format_hyperlink(
                target=info['target'],
                text=title or info['replace'],
                sub_override=ref_id,
                force_subs=True
            )
            self.substitutions[rst_src][ref_id] = subs

            rst = re.sub(  # Replace cross-ref with substitution
                pattern = rf"(?<![^\s{BEFORE_XREF}]){escape_rst(full_xref)}(?=[\s{AFTER_XREF}]|\Z)",
                repl=link,
                string=rst
            )
        return rst

    def replace_py_xrefs(self, rst_src: str, rst: str) -> str:
        """Replace |py_domain| cross-references with substitutions

        These substitutions will be hyperlinked to the corresponding source code
        or HTML documentation entry, depending on the value of
        :confval:`readme_docs_url_type`

        .. note: External attributes are always hyperlinked, but attributes for your
           own package will only be hyperlinked if linking to HTML documentation

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        xrefs = set()
        targets = {
            'regular': {
                'xrefs': [],
                'repl': r"|.\4|_"  # Replace with |.{ref_id}|_
            },
            'title': {
                'xrefs': [],
                'repl': r"|.\5+\4|_"  # Replace with |.{ref_id}+{title}|_
            }
        }
        # Find all :ref_role:`ref_id` or :ref_role:`title <ref_id>` cross-refs
        for pattern in self.get_xref_regex("py"):
            xrefs.update(re.findall(
                pattern=pattern,
                string=rst))

        for xref in xrefs:
            if len(xref) == 5:  # From title pattern
                full_xref, external, role, title, ref_id = xref
            else:
                full_xref, external, role, ref_id, *title = xref

            if not (info := self.ref_map.get(ref_id)):
                continue

            if title:  # Include explicit title in substitution name
                targets['title']['xrefs'].append(ref_id)
                ref_id = f"{ref_id}+{title}"

                if self.config.inline_markup:
                    title = f"``{title}``"

            else:
                targets['regular']['xrefs'].append(ref_id)

            link, subs = format_hyperlink(
                target=info['target'],
                text=title or info['replace'],
                sub_override=f".{ref_id}",
                force_subs=True
            )
            self.substitutions[rst_src][ref_id] = subs

        # Replace cross-refs with substitutions
        for xref_type, xref_data in targets.items():
            if xrefs := xref_data['xrefs']:
                rst = re.sub(
                    pattern=self.get_xref_regex("py", targets=xrefs, xref_type=xref_type),
                    repl=xref_data['repl'],
                    string=rst
                )
        return rst

    def replace_unresolved_xrefs(self, rst: str) -> str:
        """Replaces any unresolved cross-references from all domains with inline literals"""
        # Replace unresolved Python cross-refs
        roles = self.roles['py'].copy()

        if not self.config.replace_attrs:
            roles.remove('attr')

        rst = replace_xrefs(rst, roles)

        # Replace unresolved cross-refs from Standard and RST domain
        for pattern in self.get_xref_regex(domains=["rst", "std"]):
            rst = re.sub(
                pattern=pattern,
                repl=r"``\4``",  # Target or explicit title
                string=rst
            )
        return rst

    def get_xref_regex(self,
                       domains: str | Iterable[str],
                       roles: Optional[str | Iterable[str]] = None,
                       targets: Optional[str | Iterable[str]] = None,
                       xref_type: Optional[str] = None) -> str | Tuple[str, str]:
        """Returns the regex to match cross-references

        .. note:: The patterns have the following match groups:

           :Regular Cross-References:

              1. The full cross-reference
              2. The external role, if present
              3. The cross-reference role
              4. The cross-reference target

           :Explicit Title Cross-References:

              1. The full cross-reference
              2. The external role, if present
              3. The cross-reference role
              4. The explicit title
              5. The cross-reference target

        :param domains: an individual or list of Sphinx object domains to match
        :param roles: an individual or list of cross-reference roles to match; matches all domain roles if not provided
        :param targets: an individual or list of targets to match; matches all xrefs if not provided
        :param xref_type: the xref type to match (``"regular"`` or ``"title"``); returns both if not specified
        :return: the regex pattern to match regular xrefs, xrefs with explicit titles, or a tuple containing both
        """
        if targets is None:  # Match every cross-reference
            targets = r"~?\.?[\w./: -]+"

        if isinstance(targets, str):
            targets = [targets]

        targets = f"({'|'.join(targets)})"

        if isinstance(domains, str):
            domains = [domains]

        if roles:
            if isinstance(roles, str):
                roles = [roles]
        else:
            roles = [role for domain in domains for role in self.roles[domain]]
            if "py" in domains and self.config.replace_attrs is False:
                roles.remove("attr")

        roles = "|".join(roles)
        domains = "|".join(domains)

        xref_pattern = fr"(?<![^\s{BEFORE_XREF}])(:(?:(external(?:\+\w+)?):)?(?:(?:{domains}):)?({roles}):`{targets}`)(?=[\s{AFTER_XREF}]|\Z)"
        xref_title_pattern = fr"(?<![^\s{BEFORE_XREF}])(:(?:(external(?:\+\w+)?):)?(?:(?:{domains}):)?({roles}):`([^`]+?)\s<{targets}>`)(?=[\s{AFTER_XREF}]|\Z)"

        if xref_type == "regular":
            return xref_pattern
        elif xref_type == "title":
            return xref_title_pattern
        else:
            return xref_pattern, xref_title_pattern

    def get_admonition_regex(self, admonition: Dict[str, str]) -> str:
        """Returns the regex to match a specific admonition directive

        :param admonition: a dict containing admonition data
        """
        body = escape_rst(admonition['body']).replace('\n', r'\n\s*')
        title = escape_rst(admonition['title'])

        if admonition['type'] == 'specific':
            # For example, .. note:: This is a note
            pattern = fr"\.\. {admonition['class']}::\n*?\s+"

        else:  # Generic admonition directives with/without class option
            pattern = rf"\.\. admonition::\s+{title}" + r"\n"

            if cls := admonition['class']:
                if 'admonition-' not in cls:
                    pattern += rf"\s+:class: {cls}" + r"\n"

            pattern += r"\n*?\s+"

        if not self.config.raw_directive:
            # list-table template body uses match group
            pattern = rf"([ ]*){pattern}({body})(?=\n*(?:\1)?"
        else:
            # raw html template body uses string formatting
            pattern += rf"{body}(?=\n*"

        pattern += r"(?:\S+|\Z))"
        return pattern

    def get_admonition_icon(self, admonition: dict) -> str:
        """Returns the icon to use for an admonition

        :param admonition: a dict of admonition data
        """
        if icon := self.config.icon_map.get(admonition['class']):
            return icon
        else:
            return self.config.default_admonition_icon
