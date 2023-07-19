import re
import copy
from pathlib import Path
from collections import defaultdict
from functools import cached_property
from typing import Dict, List, Set, Union, Callable, Optional

from docutils import nodes
from sphinx import addnodes
from sphinx.testing import restructuredtext
from sphinx.domains.python import ObjectEntry
from sphinx.transforms import SphinxTransformer
from sphinx.application import Sphinx, BuildEnvironment

from sphinx_readme.config import READMEConfig
from sphinx_readme.utils.sphinx import get_conf_val
from sphinx_readme.utils.rst import get_all_xref_variants, escape_rst, format_rst, replace_attrs


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
        self.admonitions: Dict[str, Dict[str, List[Dict]]] = {}
        #: Mapping of docnames to their parsed titles
        self.titles: Dict[str, str] = {}
        #: Standard cross-reference roles
        self.roles: Set[str] = {"doc", "ref"}

    def parse_env(self, env: BuildEnvironment) -> None:
        """Parses domain data and document titles from the :class:`~.BuildEnvironment`"""
        self.parse_titles(env)
        self.parse_py_domain(env)
        self.parse_std_domain(env)

    def parse_titles(self, env: BuildEnvironment) -> None:
        """Parses document titles from the :class:`~.BuildEnvironment`"""
        for docname, title_node in env.titles.items():
            parts = []

            for child in title_node.children:
                text = child.astext()
                if isinstance(child, nodes.literal):
                    parts.append(f"``{text}``")
                else:
                    parts.append(text)

            self.titles[docname] = ' '.join(parts)

    def parse_std_domain(self, env) -> None:
        """Parses cross-reference data from the Standard domain"""
        domain = env.get_domain("std")
        self.roles.update(set(domain.object_types))

        for ref_id, text, role, docname, anchor, _ in domain.get_objects():
            replace = self.titles.get(ref_id) or text
            target = f"{self.config.html_baseurl}/{docname}.html"

            if anchor:
                target += f"#{anchor}"

            if role == "label":
                role = "ref"

            self.ref_map.setdefault(role, {})[ref_id] = {
                "replace": replace,
                "target": target
            }

    def parse_py_domain(self, env) -> None:
        """Parses cross-reference data for objects in the Python domain"""
        py_objects = env.domaindata.get('py', {}).get("objects", {})
        linkcode_resolve = get_conf_val(env, "linkcode_resolve")

        for qualname, entry in py_objects.items():
            if target := self.get_py_target(entry, linkcode_resolve):
                self.add_variants(
                    qualified_name=qualname,
                    target=target,
                    is_callable=entry.objtype in ("method", "function"))

    def get_py_target(self, entry: ObjectEntry, linkcode_resolve: Optional[Callable] = None) -> Optional[str]:
        """Resolves the target for a cross-reference to an object in the Python domain

        :param entry: the :class:`ObjectEntry` for the object
        :param linkcode_resolve: function to resolve targets when linking to source code
        :return: the link to the object's corresponding documentation entry or highlighted source code
        """
        if self.config.docs_url_type == "html":
            # All links to html documentation follow the same format
            return f"{self.config.html_baseurl}/{entry.docname}.html#{entry.node_id}"

        # Links to source code depend on the object type
        if entry.objtype in ("property", "attribute", "data", "decorator"):
            return None  # Cannot link to source code

        if entry.objtype == "module":  # Link to the file in the repository
            filepath = entry.node_id.removeprefix("module-").replace(".", "/")
            return f"{self.config.blob_url}/{filepath}.py"

        # For class/meth/func, use linkcode_resolve
        info = dict.fromkeys(("module", "fullname"))
        parts = entry.node_id.split('.')

        # TODO: look into autoexception and autodecorator
        if entry.objtype in ("class", "function"):
            info["module"] = '.'.join(parts[:-1])
            info['fullname'] = parts[-1]

        elif entry.objtype == "method":
            info["module"] = '.'.join(parts[:-2])
            info['fullname'] = '.'.join(parts[-2:])

        return linkcode_resolve("py", info)

    def add_variants(self, qualified_name: str, target: str, is_callable: bool = False):
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
        """Parses cross-reference, admonition, and toctree data from a resolved doctree"""
        # If a source has ``only`` directives, its doctree will have missing/extra content
        # Replace the ``only`` directives, then generate a new doctree to parse if needed
        doctree = self.get_doctree(app, doctree, docname)

        if doctree.get('source') in self.sources:
            self.parse_intersphinx_nodes(doctree)
            self.parse_admonitions(doctree)
            self.parse_toctrees(doctree)

    def get_doctree(self, app: Sphinx, doctree: nodes.document, docname: str) -> nodes.document:
        """Generates and resolves a new doctree for :attr:`~.src_files`
        that contain :rst:dir:`only` directives
        """
        # Return original doctree if file is not a readme source
        if (src := doctree.get('source')) not in self.sources:
            return doctree

        # Parse ``only`` directives to get true source rst of README version
        parsed_rst = self.config.read_rst(src, replace_only=True)
        raw_rst = self.sources[src]

        # Return original doctree if file had no ``only`` directives
        if parsed_rst == raw_rst:
            return doctree

        self.sources[src] = parsed_rst

        # Use temp docname to avoid duplicate warnings
        docname = docname + "_readme"

        # Generate new doctree from parsed rst using Sphinx application
        doctree = restructuredtext.parse(app, parsed_rst, docname)

        # Resolve references in the doctree
        try:
            backup = copy.deepcopy(app.env.temp_data)
            app.env.temp_data['docname'] = docname

            transformer = SphinxTransformer(doctree)
            transformer.set_environment(app.env)
            transformer.add_transforms(app.registry.get_post_transforms())
            transformer.apply_transforms()

        finally:
            app.env.temp_data = backup

        # Replace temp source with actual source
        doctree['source'] = src
        return doctree

    def parse_intersphinx_nodes(self, doctree: nodes.document) -> None:
        """Parses :mod:`sphinx.ext.autodoc` cross-references that utilize :mod:`sphinx.ext.intersphinx`

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        for node in doctree.findall(nodes.literal):
            if not isinstance(node.parent, nodes.reference):
                continue

            if node.parent.get('internal') is True:
                continue

            if 'py' not in node['classes']:
                continue

            pattern = r":(mod|class|meth|func|attr):`~?\.?[.\w]+`"
            match = re.match(pattern, node.rawsource)
            target = node.parent.get('refuri')

            if not all((match, target)):
                continue

            is_callable = match.group(1) in ("meth", "func")
            qualified_name = target.split("#")[-1].split("-")[-1]
            self.add_variants(qualified_name, target, is_callable)

    def parse_toctrees(self, doctree: nodes.document) -> None:
        """Parses the caption and entry data from :class:`~.sphinx.addnodes.toctree` nodes

        .. caution:: Toctrees are currently parsed as if the directive has the ``:titlesonly:`` option

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        source = doctree.get('source')
        for toctree in list(doctree.findall(addnodes.toctree)):
            toc = {
                'caption': toctree.get('caption'),
                'entries': []
            }
            for _, entry in toctree.get('entries', []):
                toc['entries'].append({
                    'entry': entry,
                    'title': self.titles.get(entry),
                })
            self.toctrees[source].append(toc)

    def parse_admonitions(self, doctree: nodes.document) -> None:
        """Parses data from generic and specific admonitions

        :param doctree: the doctree from one of the :attr:`~.src_files`
        """
        admonitions = {'generic': [], 'specific': []}
        src = doctree.get('source')

        for admonition in list(doctree.findall(nodes.Admonition)):
            info = {
                'body': admonition.rawsource
            }
            if isinstance(admonition, nodes.admonition):
                # Generic Admonition (using admonition directive)
                info.update({
                    'class': admonition.get('classes')[0],
                    'title': admonition.children[0].rawsource
                })
                admonitions['generic'].append(info)
            else:
                # Specific Admonition (for example, .. note::)
                info.update({
                    'class': admonition.tagname,
                    'title': admonition.tagname.title(),
                })
                admonitions['specific'].append(info)

        self.admonitions[src] = admonitions

    def resolve(self) -> None:
        """Uses parsed data from to replace cross-references and directives in the :attr:`~.src_files`

        Once resolved, files are written to the :attr:`~.out_dir`.
        """
        for src, rst in self.sources.items():
            # Replace everything using parsed data
            rst = self.replace_admonitions(src, rst)
            rst = self.replace_rst_images(src, rst)
            rst = self.replace_toctrees(src, rst)
            rst = self.replace_rst_rubrics(rst)
            rst = self.replace_py_xrefs(rst)

            for role in self.roles:
                rst = self.replace_std_xrefs(role, rst)

            # Use ref_map to generate autodoc substitution definitions
            header_vals = self.get_header_vals()

            # Write the final output
            rst_out = Path(self.config.out_dir, Path(src).name)

            with open(rst_out, 'w', encoding='utf-8') as f:
                f.write(
                    "\n".join(header_vals) + "\n\n" + rst)
            print(
                f'``sphinx_readme``: saved generated .rst file to {rst_out}')

    def replace_admonitions(self, rst_src: str, rst: str) -> str:
        """Replaces generic and specific admonition directives with HTML tables or :rst:dir:`csv-table`
        directives, depending on the value of :confval:`readme_raw_directive`

        .. admonition:: Customizing Admonitions
           :class: about

           The :attr:`~.icon_map` can be overriden to use custom admonition icons/classes

           * See :confval:`readme_admonition_icons` and :confval:`readme_default_admonition_icon`

        :param rst_src: absolute path of the source file
        :param rst: content of the source file
        """
        admonitions = self.admonitions[rst_src]

        for _type in ('generic', 'specific'):
            for admonition in admonitions[_type]:
                if pattern := self.get_admonition_regex(admonition, _type):
                    icon = self.get_admonition_icon(admonition)
                    if not self.config.raw_directive:
                        rst = re.sub(
                            pattern=pattern,
                            repl=self.config.admonition_template.format(
                                title=admonition['title'],
                                icon=icon),
                            string=rst
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
            substitutions = []
            repl = ""

            if info['caption']:
                repl += f"**{info['caption']}**\n\n"

            for entry in info['entries']:
                # Replace each entry with a link to html docs
                target = f"{self.config.html_baseurl}/{entry['entry']}.html"

                if "`" in entry['title']:
                    # Inline markup in links must be inserted with substitutions
                    sub = entry['title'].replace('`', '')
                    substitutions.extend([
                        f".. |{sub}| replace:: {entry['title']}",
                        f".. _{sub}: {target}"
                    ])
                    repl += f"* |{sub}|_\n"

                else:
                    # Replace with a normal link otherwise
                    repl += f"* `{entry['title']} <{target}>`_\n"

            if substitutions:
                repl += '\n' + '\n'.join(substitutions) + '\n'

            # Replace toctree directive with links and substitution defs
            rst = rst.replace(toctree, repl)

        return rst

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

    def replace_rst_rubrics(self, rst: str) -> str:
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

        :param rst: content of the source file
        """
        heading_chars = '!"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~'
        rubric_pattern = r'\.\. rubric:: (.+?)(?=\n)'

        if heading := self.config.rubric_heading:
            if heading in heading_chars:
                return re.sub(
                    pattern=rubric_pattern,
                    repl=lambda m: f"{m.group(1)}\n{heading * len(m.group(1))}",
                    string=rst
                )
        return re.sub(
            pattern=rubric_pattern,
            repl=lambda m: format_rst("bold", m.group(1)),
            string=rst
        )

    def replace_std_xrefs(self, ref_role: str, rst: str) -> str:
        """Replaces cross-references from the :external+sphinx:ref:`Standard Domain <domains-std>`

        .. hint::

           This includes cross-references using the :rst:role:`doc`
           or :rst:role:`ref` role, as well as any custom objects added by
           :meth:`Sphinx.add_object_type() <sphinx.application.Sphinx.add_object_type>`

        :param ref_role: the name of the cross-reference role
        :param rst: content of the source file
        """
        # Find all :ref_role:`ref_id` or :ref_role:`title <ref_id>` cross-refs
        xrefs = re.findall(
            pattern=fr"(?:\s*?):{ref_role}:`(([^`]+?)(?:\s<([\w./]+?)>)?)`(?=\s*?)",
            string=rst
        )
        for xref in xrefs:
            if not(all(xref)):  # :ref_role:`ref_id` ->  ('ref_id', 'ref_id', '')
                ref, ref_id, title = xref

            else:  # :ref_role:`title <ref_id>` -> ('title <ref_id>', 'title', 'ref_id')
                ref, title, ref_id = xref

            # Match these ids up with target data in the ref_map
            if info := self.ref_map.get(ref_role, {}).get(ref_id, {}):
                # Replace cross-refs with `text <link>`_ format
                rst = re.sub(
                    pattern=rf":{ref_role}:`{escape_rst(ref)}`",
                    repl=f"`{title or info['replace']} <{info['target']}>`_",
                    string=rst
                )
        return rst

    def replace_py_xrefs(self, rst: str) -> str:
        """Replace :mod:`~sphinx.ext.autodoc` cross-references with substitutions

        These substitutions will be hyperlinked to the corresponding source code
        or HTML documentation entry, depending on the value of
        :confval:`readme_docs_url_type`

        .. note: Attributes will only be hyperlinked
           if linking to HTML documentation

        :param rst: content of the source file
        """
        # To render on GitHub/PyPi/etc., we use Sphinx substitutions instead of cross-refs
        # Syntax is |.{ref}|_ or |.`{ref}`|_
        if self.config.inline_markup:
            repl = r"|.`\1`|_"
        else:
            repl = r"|.\1|_"

        # Replace cross-refs with substitutions
        rst = re.sub(self.py_xref_regex, repl, rst)

        # If linking to source code, replace :attr:`~.attribute` with ``attribute``
        if self.config.docs_url_type == "code" and self.config.replace_attrs:
            rst = replace_attrs(rst)

        return rst

    def get_header_vals(self) -> List[str]:
        """Returns a list of substitution definitions and hyperlink references to prepend to the file"""
        header = []

        for ref in self.py_xrefs:
            info = self.ref_map.get(ref)

            # Check for invalid ref
            if info is None:
                continue

            if self.config.inline_markup:
                ref = f"`{ref}`"

            header.extend([
                f".. |.{ref}| replace:: {info['replace']}",
                f".. _.{ref}: {info['target']}"
            ])

        if not self.config.raw_directive:
            for _type, icon in self.config.icon_map.items():
                header.append(f'.. |{_type}| replace:: {icon}')

        return header

    @cached_property
    def py_xrefs(self) -> Set[str]:
        """Python domain cross-reference targets found within source files"""
        xrefs = set()
        for src, rst in self.sources.items():
            xrefs.update(
                set(re.findall(self.py_xref_regex, rst)))
        return xrefs

    @cached_property
    def py_xref_regex(self) -> str:
        """The regular expression to match Python domain cross-references"""
        roles = r"mod|class|meth|func"
        # If linking to HTML docs, we can generate cross-refs for attributes
        if self.config.docs_url_type == "html":
            if self.config.replace_attrs:
                roles += "|attr"

        return rf":(?:{roles}):`(~?\.?[.\w]+)`"

    def get_admonition_regex(self, admonition: Dict[str, str], admonition_type: str) -> str:
        """Returns the regex to match a specific admonition directive

        :param admonition: a dict containing admonition data
        :param admonition_type: ``"generic"`` or ``"specific"``
        """
        body = escape_rst(admonition['body'])
        title = escape_rst(admonition['title'])

        # Account for arbitrary whitespace before each line of directive content
        lines = (line.replace('\n', '\n\s+') for line in body.split('\n\n'))
        body = '\n\n\s+'.join(lines)

        if admonition_type == 'specific':
            # For example, .. note:: This is a note
            pattern = fr"\.\. {admonition['class']}::\n*?\s+"

        else:
            # Generic admonition directives with/without class option
            pattern = rf"\.\. admonition::\s+{title}" + r"\n"

            if cls := admonition['class']:
                if 'admonition-' not in cls:
                    pattern += rf"\s+:class: {cls}" + r"\n"

            pattern += r"\n*?\s+"

        if not self.config.raw_directive:
            # csv-table template body uses match group
            pattern += rf"({body})"
        else:
            # raw html template body uses string formatting
            pattern += rf"{body}"

        pattern += r"(?=[\n\S]+?)"
        return pattern

    def get_admonition_icon(self, admonition: dict):
        """Returns the icon to use for an admonition

        :param admonition: a dict of admonition data
        """
        icon = self.config.icon_map.get(admonition['class'])

        # Raw directive allows for using icon directly
        if self.config.raw_directive:
            return icon if icon else self.config.default_admonition_icon

        if icon:  # Without raw directive, must use substitution
            return f"|{admonition['class']}|"

        # Use default icon if admonition class isn't in icon map
        return "|default|"
