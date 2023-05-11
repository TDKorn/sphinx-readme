import os
import copy
import sphinx
from pathlib import Path
from docutils import nodes
from docutils.nodes import Node
from collections import defaultdict
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from .utils import get_conf_val, set_conf_val
from typing import Dict, Any, Optional, Callable, List

__version__ = "v0.0.1"


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('doctree-resolved', parse_linkcode_nodes)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_out_dir", Path(app.srcdir).parent.parent, True)

    app.setup_extension('sphinx.ext.linkcode')

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}


REFERENCE_MAPPING = {
    "internal": None,
    "external": None,
    "module": None,
    "fullname": None,
    "replace": None,
}


def parse_linkcode_nodes(app: Sphinx, doctree: Node, docname: str) -> Dict:
    """Creates a mapping of Python cross-references and their targets
    """
    refs = defaultdict(lambda: copy.deepcopy(REFERENCE_MAPPING))

    for node in list(doctree.findall(nodes.inline)):
        if 'viewcode-link' in node['classes']:
            if node.parent.get('internal') is False:
                grandparent = node.parent.parent

                try:
                    qualified_name = grandparent.get("ids")[0]
                except IndexError:
                    qualified_name = grandparent.get("module", "") + grandparent.get("fullname", "")

                internal_ref = get_internal_ref(node, qualified_name)
                short_ref = qualified_name.split(".")[-1]

                info = {
                    "external": node.parent.get("refuri"),
                    "internal": internal_ref,
                    "module": grandparent.get("module"),
                    "fullname": grandparent.get("fullname"),
                }

                is_method = grandparent.get("_toc_name", "").endswith("()")
                variants = get_all_variants(qualified_name)

                for variant in variants:
                    if variant.startswith("~"):
                        replace = short_ref
                    else:
                        replace = variant.lstrip(".")

                    if is_method:
                        replace += "()"

                    if get_conf_val(app, "readme_inline_markup"):
                        replace = f"``{replace}``"

                    refs[variant].update(info)
                    refs[variant]["replace"] = replace

    set_conf_val(app, "readme_refs", refs)
    return refs
    # if get_conf_val(app, "readme_add_linkcode_class") is True:
    #     node['classes'] = ['linkcode-link']
    #     node.children = [Text(_(f'{get_conf_val(app, "linkcode_link_text", "[source]")}'))]


def get_internal_ref(node: Node, qualified_name: str) -> str:
    """Generate internal reference URL that would be used in HTML build

    Can't just use internal reference node
        - node.get("refuri") returns incorrect html file and incorrect anchor
            Ex. when rst file name is different from python file name
            html file uses python file name which is WRONG because the html file names
            are based on the rst file names

    document.get("source") returns absolute path to rst source file -> can convert to html file and use
    fully qualified name for the anchor

    """
    rst_source = os.path.basename(node.parent.document.get("source"))
    html_file = rst_source.split(".rst")[0] + ".html"
    return html_file + f"#{qualified_name}"


def get_variants(obj: str):
    """

    >>> get_variants('mod.Class.meth')
    >>> ['mod.Class.meth', '.mod.Class.meth', '~mod.Class.meth', '~.mod.Class.meth']
    """
    return [prefix + obj for prefix in ('', '.', '~', '~.')]


def get_all_variants(fully_qualified_name: str) -> List[str]:
    """Generates a list of all possible ways to cross-reference a class/method/function

    >>> get_all_variants("sphinx_github_style.meth_lexer.TDKMethLexer.get_pkg_lexer")

    ['get_pkg_lexer', '.get_pkg_lexer', '~get_pkg_lexer', '~.get_pkg_lexer', 'TDKMethLexer.get_pkg_lexer',
    '.TDKMethLexer.get_pkg_lexer', '~TDKMethLexer.get_pkg_lexer', '~.TDKMethLexer.get_pkg_lexer',
    'meth_lexer.TDKMethLexer.get_pkg_lexer', '.meth_lexer.TDKMethLexer.get_pkg_lexer',
    '~meth_lexer.TDKMethLexer.get_pkg_lexer', '~.meth_lexer.TDKMethLexer.get_pkg_lexer',
    'sphinx_github_style.meth_lexer.TDKMethLexer.get_pkg_lexer',
     '.sphinx_github_style.meth_lexer.TDKMethLexer.get_pkg_lexer',
     '~sphinx_github_style.meth_lexer.TDKMethLexer.get_pkg_lexer',
      '~.sphinx_github_style.meth_lexer.TDKMethLexer.get_pkg_lexer']

    :param fully_qualified_name: the fully qualified name (pkg.module.class.method)
    """
    parts = fully_qualified_name.split(".")[::-1]  # => ['meth', 'Class', 'mod', "pkg"]
    variants = []

    for i, part in enumerate(parts):
        ref = '.'.join(parts[i::-1])  # 'meth', 'Class.meth', 'mod.class.meth', 'pkg.mod.class.meth'
        variants.extend(get_variants(ref))

    return variants
