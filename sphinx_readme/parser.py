import os
import re
from typing import Dict

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

    def parse_references(self, doctree: Node, docname: str):
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
            body = admonition.rawsource
            sep = admonition.child_text_separator
            lines = body.split(sep)
            info = dict(
                body=body,
                startswith=lines[0],
                endswith=lines[-1]
            )
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

    def replace_admonitions(self):
        for src, admonitions in self.admonitions.items():
            rst = self.config.readme_sources[src]

            for _type in ('generic', 'specific'):
                for admonition in admonitions[_type]:
                    pattern = self.get_admonition_regex(admonition, _type, rst)
                    icon = self.get_admonition_icon(admonition, _type)
                    rst = re.sub(
                        pattern=pattern,
                        repl=self.config.admonition_template.format(
                            title=admonition['title'],
                            icon=admonition['class'],
                            text=admonition['body']
                        ),
                        string=rst
                    )

            self.config.readme_sources[src] = rst

    def get_admonition_regex(self, admonition, admonition_type, rst):
        if not (rst_body := self.find_admonition_body(admonition, rst)):
            return ''

        if admonition_type == 'specific':
            # For example, .. note:: This is a note
            pattern = fr".. {admonition['title']}::\n?\n?\s+{rst_body}"

        else:
            # Any admonition that uses generic .. admonition:: directive
            pattern = rf".. admonition:: {admonition['title']}" + r"\n"

            if cls := admonition['class']:
                if 'admonition-' not in cls:
                    pattern += rf"\s+:class: {cls}" + r"\n"

            pattern += r"\n" + rf"\s+{rst_body}"

        return pattern

    def find_admonition_body(self, admonition: Dict, rst: str) -> str:
        """Return the exact ``rst`` corresponding to the body of the admonition"""
        startswith = admonition['startswith']
        endswith = admonition['endswith']

        if not (startswith in rst and endswith in rst):
            return ''

        start = rst.find(startswith)
        end = rst.find(endswith) + len(endswith)
        body = rst[start:end]

        return body.replace("*", r"\*").replace("+", r"\+").replace(".", r"\.").replace("?", r"\?")

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

    def resolve_readme(self, exception):
        print("RESOLVING THE README ")
        input()


def parse_references(app: Sphinx, doctree: Node, docname: str) -> Dict:
    readme = get_conf_val(app, 'READMEParser')
    readme.parse_references(doctree, docname)


def resolve_readme(app: Sphinx, exception):
    readme = get_conf_val(app, 'READMEParser')
    readme.resolve_readme(exception)