import os
from typing import Dict

from docutils import nodes
from docutils.nodes import Node
from sphinx.application import Sphinx

from sphinx_readme.config import READMEConfig
from sphinx_readme.utils import get_conf_val, set_conf_val, get_all_variants


class READMEParser:

    def __init__(self, app: Sphinx):
        self.config = READMEConfig(app)
        self.ref_map = self.config.ref_map

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


    def parse_linkcode_node(self, node: Node):
        grandparent = node.parent.parent

        try:
            qualified_name = grandparent.get("ids")[0]
        except IndexError:
            qualified_name = grandparent.get("module", "") + grandparent.get("fullname", "")

        short_ref = qualified_name.split(".")[-1]
        is_method = grandparent.get("_toc_name", "").endswith("()")

        if self.config.docs_url_type == "code":
            target = node.parent.get("refuri")
        else:
            target = self.get_internal_target(node, qualified_name)

        info = {
            "target": target,
            "module": grandparent.get("module"),
            "fullname": grandparent.get("fullname"),
        }
        variants = get_all_variants(qualified_name)

        for variant in variants:
            if variant.startswith("~"):
                replace = short_ref
            else:
                replace = variant.lstrip(".")

            if is_method:
                replace += "()"

            if self.config.inline_markup:
                replace = f"``{replace}``"

            info["replace"] = replace
            self.config.ref_map[variant].update(info)

    def parse_attr_node(self, node: Node):
        try:
            child = node.children[0]
        except (AttributeError, IndexError) as e:
            return

        if isinstance(child, nodes.literal) and 'py-attr' in child.get('classes', []):
            refuri = node.get("refuri", '').lstrip('./')
            qualified_name = node.get("reftitle")

            if not all((refuri, qualified_name)):
                return

            target = self.config.docs_url + "/" + refuri
            short_ref = qualified_name.split('.')[-1]
            variants = get_all_variants(qualified_name)

            for variant in variants:
                if variant.startswith("~"):
                    replace = short_ref
                else:
                    replace = variant.lstrip('.')

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

    def resolve_readme(self, exception):
        print("RESOLVING THE README ")
        input()


def parse_references(app: Sphinx, doctree: Node, docname: str) -> Dict:
    readme = get_conf_val(app, 'READMEParser')
    readme.parse_references(doctree, docname)


def resolve_readme(app: Sphinx, exception):
    readme = get_conf_val(app, 'READMEParser')
    readme.resolve_readme(exception)