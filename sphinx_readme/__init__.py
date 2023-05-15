import os
import copy
import re
import sphinx
from pathlib import Path
from docutils import nodes
from docutils.nodes import Node
from collections import defaultdict
from sphinx.application import Sphinx
from sphinx.errors import ExtensionError
from .utils import get_conf_val, set_conf_val, read_rst
from typing import Dict, Any, Optional, Callable, List

__version__ = "v0.0.1"


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('doctree-resolved', parse_references)
    app.connect('build-finished', resolve_readme)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_replace_attrs", True, True)
    app.add_config_value("readme_out_dir", Path(app.srcdir).parent.parent, True)

    app.setup_extension('sphinx.ext.linkcode')

    docs_url = get_conf_val(app, "readme_docs_url")
    if docs_url == get_conf_val(app, "linkcode_url"):
        link_type = "code"
    else:
        link_type = "html"

    set_conf_val(app, "readme_link_type", link_type)

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}


REFERENCE_MAPPING = {
    "module": None,
    "fullname": None,
    "replace": None,
    "target": None
}


def parse_references(app: Sphinx, doctree: Node, docname: str) -> Dict:
    """Creates a mapping of Python cross-references and their targets
    """
    docs_url = get_conf_val(app, "readme_docs_url", get_conf_val(app, "linkcode_url", "")).rstrip("/")
    if not docs_url:
        raise ExtensionError(
            "sphinx_readme: ``readme_docs_url`` or ``linkcode_url`` must be set"
        )
    link_type = get_conf_val(app, "readme_link_type")
    refs = get_conf_val(app, "readme_refs")

    if refs is None:
        refs = defaultdict(lambda: copy.deepcopy(REFERENCE_MAPPING))
        refs['std-ref'] = []



    for node in list(doctree.findall(nodes.inline)):
        if 'std-ref' in node['classes']:
            target = {
                "text": str(node.children[0]),
                "refuri": get_conf_val(app, "html_baseurl", "") + node.parent.get('refuri', '')
            }
            refs['std-ref'].append(target)

        elif 'viewcode-link' in node['classes'] or 'linkcode-link' in node['classes']:
            if node.parent.get('internal') is False:
                grandparent = node.parent.parent
                try:
                    qualified_name = grandparent.get("ids")[0]
                except IndexError:
                    qualified_name = grandparent.get("module", "") + grandparent.get("fullname", "")

                short_ref = qualified_name.split(".")[-1]
                is_method = grandparent.get("_toc_name", "").endswith("()")

                if link_type == "code":
                    target = node.parent.get("refuri")
                else:
                    target = get_internal_ref(node, docs_url, qualified_name)

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

                    if get_conf_val(app, "readme_inline_markup"):
                        replace = f"``{replace}``"

                    info["replace"] = replace
                    refs[variant].update(info)

    set_conf_val(app, "readme_refs", refs)
    return refs
    # if get_conf_val(app, "readme_add_linkcode_class") is True:
    #     node['classes'] = ['linkcode-link']
    #     node.children = [Text(_(f'{get_conf_val(app, "linkcode_link_text", "[source]")}'))]


def resolve_readme(app: Sphinx, exception):
    rst_files = get_conf_val(app, "readme_src", [])
    out_dir = get_conf_val(app, "readme_out_dir")
    parse_include_directive = get_conf_val(app, "readme_include_directive")
    use_raw_directive = get_conf_val(app, "readme_raw_directive")
    docs_url = get_conf_val(app, "readme_docs_url", get_conf_val(app, "linkcode_url"))

    if isinstance(rst_files, str):
        rst_files = [rst_files]

    rst_files = [
        # Absolute path of files; files should be relative to source directory
        str((Path(app.srcdir) / Path(rst_file)).resolve())
        for rst_file in rst_files
    ]
    # Create dict of {file: text} - all parsing is done on this text
    rst_sources = {
        rst_file: read_rst(str(rst_file), parse_include_directive)
        for rst_file in rst_files
    }

    if not os.path.exists(out_dir):
        os.mkdir(out_dir)

    ref_map = get_conf_val(app, "readme_refs")

    for rst_src in rst_sources:
        rst = resolve_autodoc_refs(
            rst=rst_sources[rst_src],
            ref_map=ref_map,
            inline_markup=get_conf_val(app, "readme_inline_markup")
        )

        if get_conf_val(app, "readme_replace_attrs"):
            rst = replace_autodoc_attrs(rst)

        rst = replace_rst_images(
            src_dir=app.srcdir,
            out_dir=out_dir,
            rst_src=rst_src,
            rst=rst
        )
        rst = replace_std_refs(rst, ref_map)

        rst_out = os.path.join(
            out_dir, os.path.basename(rst_src)
        )
        with open(rst_out, 'w', encoding='utf-8') as f:
            f.write(rst)
        print(
            f'``sphinx_readme``: saved generated .rst file to {rst_out}')


def get_internal_ref(node: Node, docs_url: str, qualified_name: str) -> str:
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
    return f"{docs_url}/{html_file}#{qualified_name}"

def replace_std_refs(rst, ref_map):
    # Find all :ref:`ref_id` cross-refs
    std_cross_refs = re.findall(
        pattern=r":ref:`(.+)`",
        string=rst
    )
    # Match these ids up with target data in the ref_map
    std_refs = dict(zip(std_cross_refs, ref_map['std-ref']))

    # Replace cross-refs with `text <link>`_ format
    for ref_id, info in std_refs.items():
        rst = re.sub(
            pattern=rf":ref:`{ref_id}`",
            repl=rf"`{info['text']} <{info['refuri']}>`_",
            string=rst
        )
    return rst


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


def resolve_autodoc_refs(rst, ref_map, inline_markup):
    # The rst could have :directive:`{~.}{module|class}{.}target` where {} is optional
    # Directives to link to source code -> class, meth, func
    pattern = rf":(?:class|meth|func):`([~\.\w]+)`"

    # Sphinx substitutions are used for cross-refs instead
    # Syntax is |.{ref}|_ or |.`{ref}`|_
    if inline_markup:
        repl = r"|.`\1`|_"
    else:
        repl = r"|.\1|_"

    # Get a list of all autodoc cross-refs
    autodoc_refs = set(re.findall(pattern, rst))

    # Replace cross-refs with substitutions
    rst = re.sub(pattern, repl, rst)

    # Use ref_map to generate header for cross-refs in the file
    header = get_header_vals(autodoc_refs, ref_map, inline_markup, link_type="code")

    rst = "\n".join(header) + "\n\n" + rst
    return rst


def get_header_vals(autodoc_refs, ref_map, inline_markup, link_type) -> List[str]:
    header = []

    for ref in autodoc_refs:
        info = ref_map[ref]

        # Check for empty REFERENCE_MAPPING
        if not any(info.values()):
            continue

        if inline_markup:
            ref = f"`{ref}`"

        header.extend([
            f".. |.{ref}| replace:: {info['replace']}",
            f".. _.{ref}: {info['target']}"
        ])

    return header


def replace_autodoc_attrs(rst) -> str:
    # Ex. ~.Class.meth => ``meth``
    short_ref = r" :attr:`~\.?(\w+)`"
    # Ex. .Class.meth => ``Class.meth``
    long_ref = r" :attr:`\.?([\.\w]+)`"
    repl = r" ``\1``"

    rst = re.sub(short_ref, repl, rst)
    rst = re.sub(long_ref, repl, rst)
    return rst


def replace_rst_images(src_dir: str, out_dir: str, rst_src: str, rst: str) -> str:
    """Resolves filepaths of ``image`` directives to be relative to the ``readme_out_dir`` instead of the ``source`` dir

        ".. image:: /blah/blah.png"
        ".. image:: /blah.png"
        ".. image:: blah.png"
        ".. image:: blah/blah.png"
        ".. image:: ../blah/blah.png"

    :param src_dir: the Sphinx docs source directory (``app.srcdir``)
    :param out_dir: the output directory for the rst file
    :param rst_src: filename of the rst file being parsed
    :param rst: the content of the rst file being parsed
    :return: the rst file content with correct image directives
    """
    out_dir_path = Path(out_dir)
    rst_src_dir = Path(rst_src).parent

    # These image paths are relative to the rst source file
    # .. image:: image.png || .. image:: images/image.png || .. image:: ../images/image.png
    relative = r".. image:: ([\w\.]+[\w/]+\.\w{3,4})"
    matches = re.findall(relative, rst)

    for match in matches:
        # Find absolute path of the image
        rel_img_path = Path(match)
        abs_img_path = (rst_src_dir / rel_img_path).resolve()
        # Find path of image relative to the output directory
        final_img_path = str(abs_img_path.relative_to(out_dir_path)).replace(os.path.sep, "/")
        # Sub that hoe in!!!
        rst = re.sub(
            pattern=rf".. image:: {match}",
            repl=fr".. image:: {final_img_path}",
            string=rst
        )
    # These image paths are "absolute" (relative to src_dir)
    # .. image:: /path/to/image.ext
    relpath_to_src = os.path.relpath(src_dir, out_dir).replace(os.path.sep, "/")
    return re.sub(
        pattern=r".. image:: (/[\w/]+\.\w{3,4})",
        repl = fr".. image:: {relpath_to_src}\1",
        string=rst
    )


def replace_admonitions(rst: str, raw_directive: bool = True) -> str:
    pattern = r".. admonition:: \w?\n\W*\w*\n+W+"
    if raw_directive:
        admonition = '''
.. raw:: html

   <table>
      <tr align="left">
         <th>{icon} {title}</th>
      </tr>
      <tr>
         <td>

{text}

.. raw:: html

   </td></tr>
   </div>

'''
    else:
        admonition = '''
.. csv-table::
    :header: {icon} {title}

    "{text}"

'''
    return admonition   # obviously not