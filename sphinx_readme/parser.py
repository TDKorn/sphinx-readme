import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

from docutils import nodes
from docutils.nodes import Node
from sphinx.application import Sphinx

from sphinx_readme.config import READMEConfig
from sphinx_readme.utils import get_conf_val, set_conf_val, get_all_variants


class READMEParser:

    def __init__(self, app: Sphinx):
        self.config = READMEConfig(app)
        self.logger = self.config.logger
        self.ref_map = self.config.ref_map
        self.admonitions = {}

    def parse(self, doctree: Node, docname: str):
        for node in list(doctree.findall(nodes.inline)):
            if 'doc' in node['classes']:
                self.ref_map['doc'].append(self.get_cross_ref_target(node))

            elif 'std-ref' in node['classes']:
                self.ref_map['ref'].append(self.get_cross_ref_target(node))

            elif 'viewcode-link' in node['classes'] or 'linkcode-link' in node['classes']:
                if node.parent.get('internal') is False:
                    self.parse_linkcode_node(node)

        if self.config.replace_attrs and self.config.docs_url_type == 'html':
            for node in list(doctree.findall(nodes.reference)):
                if ":attr:" in node.parent.rawsource:
                    self.parse_attr_node(node)

        if doctree.get('source') in self.config.readme_sources:
            self.parse_admonitions(doctree)

    def parse_linkcode_node(self, node: Node):
        grandparent = node.parent.parent
        is_method = grandparent.get("_toc_name", "").endswith("()")

        try:
            qualified_name = grandparent.get("ids")[0]
        except IndexError:
            qualified_name = grandparent.get("module", "") + grandparent.get("fullname", "")

        if self.config.docs_url_type == "code":
            target = node.parent.get("refuri")
        else:
            target = self.get_internal_target(node, qualified_name)

        self.add_variants(qualified_name, target, is_method)

    def parse_attr_node(self, node: Node):
        try:
            child = node.children[0]
        except (AttributeError, IndexError) as e:
            return

        if not isinstance(child, nodes.literal):
            return

        if 'py-attr' not in child.get('classes', []):
            return

        refuri = node.get("refuri", '').lstrip('./')
        qualified_name = node.get("reftitle")

        if not all((refuri, qualified_name)):
            return

        target = self.config.docs_url + "/" + refuri
        self.add_variants(qualified_name, target)

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

    def get_cross_ref_target(self, node: Node) -> Dict:
        """Helper function to parse target info of a :ref: or :doc: cross-reference"""
        return {
            'text': str(node.children[0]),
            "refuri": self.config.docs_url + "/" + node.parent.get('refuri', '')
        }

    def get_internal_target(self, node: Node, qualified_name: str):
        """Helper function to parse an internal target from a linkcode node"""
        rst_source = os.path.basename(node.parent.document.get("source"))
        html_file = rst_source.split(".rst")[0] + ".html"
        return f"{self.config.docs_url}/{html_file}#{qualified_name}"

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
                    'title': admonition.tagname,
                })
                admonitions['specific'].append(info)

        self.admonitions[src] = admonitions

    def resolve(self):
        for readme_src, rst in self.config.readme_sources.items():
            rst = self.replace_admonitions(readme_src, rst)

            rst = self.replace_rst_images(readme_src, rst)

            for role in ('ref', 'doc'):
                rst = self.replace_cross_refs(rst, role)

            # Use ref_map to generate header for autodoc substitutions
            rst, autodoc_refs = self.resolve_autodoc_refs(rst)
            header_vals = self.get_header_vals(autodoc_refs)

            # Write the final output
            rst_out = Path(self.config.out_dir, Path(readme_src).name)

            with open(rst_out, 'w', encoding='utf-8') as f:
                f.write(
                    "\n".join(header_vals) + "\n\n" + rst)
            print(
                f'``sphinx_readme``: saved generated .rst file to {rst_out}')

    def resolve_autodoc_refs(self, rst: str) -> Tuple[str, Dict]:
        """
        :param rst:
        :return:
        """
        # :role:`{~.}{module|class}{.}target` where {} is optional
        pattern = r":(?:class|meth|func):`([~\.\w]+)`"

        if self.config.replace_attrs:
            if self.config.docs_url_type == 'html':
                # If linking to HTML docs, we can generate cross-refs for attributes
                pattern = r":(?:class|meth|func|attr):`([~\.\w]+)`"
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

        # Use ref_map to generate header for cross-refs in the file
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

    def get_header_vals(self, autodoc_refs: Dict) -> List[str]:
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

        return header

    def replace_rst_images(self, rst_src: str, rst: str) -> str:
        """Resolves filepaths of ``image`` directives to be relative to the ``readme_out_dir``

            ".. image:: /blah/blah.png"
            ".. image:: /blah.png"
            ".. image:: blah.png"
            ".. image:: blah/blah.png"
            ".. image:: ../blah/blah.png"

        :param rst_src: filename of the rst file being parsed
        :param rst: the content of the rst file being parsed
        :return: the rst file content with correct image directives
        """
        src_dir_path = Path(self.config.src_dir)
        out_dir_path = Path(self.config.out_dir)
        rst_src_dir_path = Path(rst_src).parent

        # These image paths are relative to the rst source file
        # .. image:: image.png || .. image:: images/image.png || .. image:: ../images/image.png
        relative = r".. image:: ([\w\.]+[\w/]+\.\w{3,4})"
        img_paths = re.findall(relative, rst)

        for img_path in img_paths:
            # Find absolute path of the image
            abs_img_path = (rst_src_dir_path / Path(img_path)).resolve()

            # Find path of image relative to the output directory
            rel_img_path = abs_img_path.relative_to(out_dir_path).as_posix()

            # Sub that hoe in!!!
            rst = re.sub(
                pattern=rf".. image:: {img_path}",
                repl=fr".. image:: {rel_img_path}",
                string=rst
            )

        # These image paths are "absolute" (relative to src_dir)
        # .. image:: /path/to/image.ext
        relpath_to_src_dir = src_dir_path.relative_to(out_dir_path).as_posix()

        # Replace all image paths starting with "/"
        return re.sub(
            pattern=r".. image:: (/[\w/]+\.\w{3,4})",
            repl=fr".. image:: {relpath_to_src_dir}\1",
            string=rst
        )

    def replace_cross_refs(self, rst: str, ref_role: str) -> str:
        # Find all :ref_role:`ref_id` cross-refs
        cross_refs = re.findall(
            pattern=fr":{ref_role}:`(.+)`",
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

    def replace_admonitions(self, rst_src: str, rst: str) -> str:
        admonitions = self.admonitions[rst_src]

        for _type in ('generic', 'specific'):
            for admonition in admonitions[_type]:
                if pattern := self.get_admonition_regex(admonition, _type):
                    icon = self.get_admonition_icon(admonition, _type)
                    if not self.config.raw_directive:
                        rst = re.sub(
                            pattern=pattern,
                            repl=self.config.admonition_template.format(
                                title=admonition['title'].title(),
                                icon=icon),
                            string=rst
                        )
                    else:
                        rst = re.sub(
                            pattern=pattern,
                            repl=self.config.admonition_template.format(
                                title=admonition['title'].title(),
                                text=admonition['body'],
                                icon=icon),
                            string=rst
                        )
        return rst

    def get_admonition_regex(self, admonition, admonition_type):
        # Parse rawsource body to have same whitespace formatting as the rst file
        lines = (line.replace('\n', '\n   ') for line in admonition['body'].split('\n\n'))
        body = '\n\n   '.join(lines)

        for char in ("*", "+", ".", "?"):
            body = body.replace(char, rf"\{char}")

        if admonition_type == 'specific':
            # For example, .. note:: This is a note
            pattern = fr"\.\. {admonition['title']}::\n?\n?\s+"

        else:
            # Any admonition that uses generic .. admonition:: directive
            pattern = rf"\.\. admonition:: {admonition['title']}" + r"\n"

            if cls := admonition['class']:
                if 'admonition-' not in cls:
                    pattern += rf"\s+:class: {cls}" + r"\n"

            pattern += r"\n" + rf"\s+"

        if not self.config.raw_directive:
            # csv-table template body uses match group
            pattern += rf"({body})"
        else:
            # raw html template body uses string formatting
            pattern += rf"{body}"

        pattern += r"(\n+\S+|$)"
        return pattern


    def get_admonition_icon(self, admonition: dict, admonition_type: str):
        types = ("attention", "caution", "danger", "error", "hint", "important", "note", "tip", "warning")
        icons = ("⚠", "⚠", "☢", "❌", "🧠", "‼", "📝", "💡", "❗")
        icon_map = dict(zip(types, icons))
        icon = icon_map.get(admonition['class'], '')
        if self.config.raw_directive is True:  # Raw directive allows for using icon directly
            return icon

        if icon:  # Without raw directive, must use substitution
            # self.header.append(f".. |{admonition['class']}| replace:: {icon}")  # TODO: add header with all icon subs
            return f"|{admonition['class']}|"
        return ''


