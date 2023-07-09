import re
from copy import copy
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Set

from docutils import nodes
from docutils.nodes import Node, document

from sphinx import addnodes
from sphinx.application import Sphinx
from sphinx.testing import restructuredtext
from sphinx.transforms import SphinxTransformer
from sphinx.environment import BuildEnvironment

from sphinx_readme.config import READMEConfig
from sphinx_readme.utils import get_all_variants, escape_rst, format_rst


class READMEParser:

    def __init__(self, app: Sphinx):
        self.config = READMEConfig(app)
        self.logger = self.config.logger
        self.ref_map = self.config.ref_map
        self.sources = self.config.source_files
        self.toctrees = defaultdict(list)
        self.admonitions = {}
        self.titles = {}

    def parse(self, app: Sphinx, doctree: document, docname: str):
        # If a source has ``only`` directives, its doctree will have missing/extra content
        # Replace the ``only`` directives, then generate a new doctree if needed
        doctree = self.get_doctree(app, doctree, docname)

        inline_nodes = list(doctree.findall(nodes.inline))
        literal_nodes = list(doctree.findall(nodes.literal))

        self.parse_autodoc_nodes(literal_nodes, docname)

        if self.config.docs_url_type == "code":
            self.parse_linkcode_nodes(inline_nodes)

        for node in list(doctree.findall(addnodes.toctree)):
            self.parse_toctree(node, doctree)

        if doctree.get('source') in self.sources:
            self.parse_xref_nodes(inline_nodes)
            self.parse_admonitions(doctree)

    def get_doctree(self, app: Sphinx, doctree: document, docname: str) -> document:
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
            backup = copy(app.env.temp_data)
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

    def parse_xref_nodes(self, inline_nodes: List[nodes.inline]):
        for node in inline_nodes:
            if 'doc' in node['classes']:
                self.ref_map['doc'].append(self._parse_xref(node))

            elif 'std-ref' in node['classes']:
                self.ref_map['ref'].append(self._parse_xref(node))

    def _parse_xref(self, node: nodes.inline) -> Dict:
        """Helper function to parse target info of a ``:ref:`` or ``:doc:`` xref"""
        return {
            'text': node.children[0].astext(),
            "refuri": self.config.html_baseurl + "/" + node.parent.get('refuri', '')
        }

    def parse_autodoc_nodes(self, literal_nodes: List[nodes.literal], docname: str):
        for node in literal_nodes:
            if 'py' not in node['classes']:
                continue

            if not isinstance(node.parent, nodes.reference):
                continue

            if node.parent.get('internal') is False:
                # External links are xrefs from intersphinx
                self.parse_intersphinx_node(node)

            elif 'py-mod' in node['classes']:
                # Parse :mod: xrefs regardless of docs_url_type
                self.parse_module_node(node, docname)

            elif self.config.docs_url_type == "html":
                # Only parse remaining py xrefs if linking to html
                self.parse_autodoc_node(node, docname)

    def parse_intersphinx_node(self, node: nodes.literal):
        pattern = r":(mod|class|meth|func|attr):`~?\.?[.\w]+`"
        match = re.match(pattern, node.rawsource)
        target = node.parent.get('refuri')

        if not all((match, target)):
            return

        is_method = match.group(1) == "meth"
        qualified_name = target.split("#")[-1].split("-")[-1]
        self.add_variants(qualified_name, target, is_method)

    def parse_module_node(self, node: Node, docname: str):
        qualified_name = node.parent.get("reftitle", "")

        if self.config.docs_url_type == 'code':
            # Ex. sphinx_readme.parser -> sphinx_readme/parser.py
            refuri = qualified_name.replace('.', '/') + '.py'
        else:
            refuri = self._parse_refuri(node, docname)

        if not all((qualified_name, refuri)):
            return

        target = f"{self.config.docs_url}/{refuri}"
        self.add_variants(qualified_name, target)

    def parse_autodoc_node(self, node: nodes.literal, docname: str):
        qualified_name = node.parent.get("reftitle")
        refuri = self._parse_refuri(node, docname)

        if not all((refuri, qualified_name)):
            return

        is_method = 'py-meth' in node['classes']
        target = f"{self.config.docs_url}/{refuri}"
        self.add_variants(qualified_name, target, is_method)

    def _parse_refuri(self, node: Node, docname: str):
        if 'refuri' in node.parent:
            # Ex. ../parser.html#sphinx_readme.parser.READMEParser
            return node.parent["refuri"].lstrip("./")

        elif 'refid' in node.parent:
            # Ex. sphinx_readme.parser.READMEParser
            return f"{docname}.html#{node.parent['refid']}"

    def parse_linkcode_nodes(self, inline_nodes: List[nodes.inline]):
        for node in inline_nodes:
            if 'viewcode-link' in node['classes'] or 'linkcode-link' in node['classes']:
                if node.parent.get('internal') is False:
                    # Only parse links to external source code
                    self.parse_linkcode_node(node)

    def parse_linkcode_node(self, node: nodes.inline):
        grandparent = node.parent.parent
        is_method = grandparent.get("_toc_name", "").endswith("()")

        try:
            qualified_name = grandparent.get("ids")[0]
        except IndexError:
            qualified_name = grandparent.get("module", "") + grandparent.get("fullname", "")

        target = node.parent.get("refuri")
        self.add_variants(qualified_name, target, is_method)

    def add_variants(self, qualified_name, target, is_method: bool = False):
        short_ref = qualified_name.split('.')[-1]
        variants = get_all_variants(qualified_name)

        for variant in variants:
            if variant in self.ref_map:
                continue

            if variant.startswith("~"):
                replace = short_ref
            else:
                replace = variant.lstrip('.')

            if is_method:
                replace += "()"

            if self.config.inline_markup:
                replace = f"``{replace}``"

            self.ref_map[variant].update({
                'target': target,
                'replace': replace
            })

    def parse_titles(self, env: BuildEnvironment):
        for fname, title_node in env.titles.items():
            parts = []

            for child in title_node.children:
                text = child.astext()
                if isinstance(child, nodes.literal):
                    parts.append(f"``{text}``")
                else:
                    parts.append(text)

            self.titles[fname] = ' '.join(parts)

    def parse_toctree(self, toctree: Node, doctree: addnodes.document):
        src = doctree.get('source')
        toc = {
            'caption': toctree.get('caption'),
            'entries': []
        }
        for _, entry in toctree.get('entries', []):
            toc['entries'].append({
                'entry': entry,
                'title': self.titles.get(entry),
            })
        self.toctrees[src].append(toc)

    def parse_admonitions(self, doctree: Node):
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

    def resolve(self):
        for src, rst in self.sources.items():
            # Replace everything using data from ``parse()``
            rst = self.replace_admonitions(src, rst)
            rst = self.replace_rst_images(src, rst)
            rst = self.replace_toctrees(src, rst)
            rst = self.replace_rst_rubrics(rst)

            for role in ('ref', 'doc'):
                rst = self.replace_cross_refs(rst, role)

            # Use ref_map to generate autodoc substitution definitions
            rst, autodoc_refs = self.replace_autodoc_refs(rst)
            header_vals = self.get_header_vals(autodoc_refs)

            # Write the final output
            rst_out = Path(self.config.out_dir, Path(src).name)

            with open(rst_out, 'w', encoding='utf-8') as f:
                f.write(
                    "\n".join(header_vals) + "\n\n" + rst)
            print(
                f'``sphinx_readme``: saved generated .rst file to {rst_out}')

    def replace_admonitions(self, rst_src: str, rst: str) -> str:
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
        if self.config.docs_url_type == 'html':
            base_url = self.config.docs_url
        else:
            base_url = self.config.html_baseurl

        pattern = r".. toctree::\n+?(?:\s+:\w+:\s*?\w*?\n\s+)*?(?:\s+\w+\n)+?(?=\n+\S+?)"
        toctrees = re.findall(pattern, rst)

        for toctree, info in zip(toctrees, self.toctrees[rst_src]):
            substitutions = []
            repl = ""

            if info['caption']:
                repl += f"**{info['caption']}**\n\n"

            for entry in info['entries']:
                # Replace each entry with a link to html docs
                target = f"{base_url}/{entry['entry']}.html"

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
                repl += '\n\n' + '\n'.join(substitutions) + '\n\n'

            # Replace toctree directive with links and substitution defs
            rst = rst.replace(toctree, repl)

        return rst

    def replace_rst_images(self, rst_src: str, rst: str) -> str:
        """Replaces filepaths in ``image`` directives with repository links

        :Example:
            :rst:`.. image:: /_static/logo.png`

            would be replaced with

            :rst:`.. image:: https://github.com/tdkorn/sphinx-readme/blob/main/docs/source/_static/logo.png?raw=True`

        .. note:: Your repository will be used as the image source regardless of the
           value of :confval:`readme_docs_url_type`

        :param rst_src: absolute path of the rst file being parsed
        :param rst: the content of the rst file being parsed
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

    def replace_rst_rubrics(self, rst: str):
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

    def replace_cross_refs(self, rst: str, ref_role: str) -> str:
        # Find all :ref_role:`ref_id` cross-refs
        cross_refs = re.findall(
            pattern=fr"(?:\s*?):{ref_role}:`([^`]+)`(?=\s*?)",
            string=rst
        )
        # Match these ids up with target data in the ref_map
        cross_ref_map = dict(zip(cross_refs, self.ref_map[ref_role]))

        # Replace cross-refs with `text <link>`_ format
        for ref_id, target in cross_ref_map.items():
            rst = re.sub(
                pattern=rf":{ref_role}:`{ref_id}`",
                repl=rf"`{target['text']} <{target['refuri']}>`_",
                string=rst
            )
        return rst

    def replace_autodoc_refs(self, rst: str) -> Tuple[str, Set]:
        """
        :param rst:
        :return:
        """
        # :role:`{~.}{module|class}{.}target` where {} is optional
        pattern = r":(?:mod|class|meth|func):`([~\.\w]+)`"

        if self.config.replace_attrs:
            if self.config.docs_url_type == 'html':
                # If linking to HTML docs, we can generate cross-refs for attributes
                pattern = r":(?:mod|class|meth|func|attr):`([~\.\w]+)`"
            else:
                # If linking to source code, just replace :attr:`~.attribute` with ``attribute``
                rst = self.replace_autodoc_attrs(rst)

        # To render on GitHub/PyPi/etc., we use Sphinx substitutions instead of cross-refs
        # Syntax is |.{ref}|_ or |.`{ref}`|_
        if self.config.inline_markup:
            repl = r"|.`\1`|_"
        else:
            repl = r"|.\1|_"

        # Get a list of all autodoc cross-refs
        autodoc_refs = set(re.findall(pattern, rst))

        # Replace cross-refs with substitutions
        rst = re.sub(pattern, repl, rst)

        # Use autodoc_refs and ref_map to generate substitution definitions
        return rst, autodoc_refs

    def replace_autodoc_attrs(self, rst: str) -> str:
        # Ex. ~.Class.meth => ``meth``
        short_ref = r" :attr:`~\.?(\w+)`"
        # Ex. .Class.meth => ``Class.meth``
        long_ref = r" :attr:`\.?([\.\w]+)`"
        repl = r" ``\1``"

        rst = re.sub(short_ref, repl, rst)
        rst = re.sub(long_ref, repl, rst)
        return rst

    def get_header_vals(self, autodoc_refs: Set) -> List[str]:
        header = []

        for ref in autodoc_refs:
            info = self.ref_map[ref]

            # Check for empty REFERENCE_MAPPING
            if not any(info.values()):
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

    def get_admonition_regex(self, admonition, admonition_type):
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
        icon = self.config.icon_map.get(admonition['class'])

        # Raw directive allows for using icon directly
        if self.config.raw_directive:
            return icon if icon else self.config.default_admonition_icon

        if icon:  # Without raw directive, must use substitution
            return f"|{admonition['class']}|"

        # Use default icon if admonition class isn't in icon map
        return "|default|"
