import os
import copy
import re
import sphinx
from pathlib import Path
from sphinx.application import Sphinx
from typing import Dict, Any, Optional, Callable, List, Union
from .utils import get_conf_val, set_conf_val, read_rst, logger
from .parser import READMEParser, parse_references, resolve_readme

__version__ = "v0.0.1"


def setup(app: Sphinx) -> Dict[str, Any]:
    set_conf_val(app, 'READMEParser', READMEParser(app))

    app.connect('doctree-resolved', parser.parse_references)
    app.connect('build-finished', parser.resolve_readme)
    # app.connect('doctree-resolved', parse_references)
    # app.connect('build-finished', resolve_readme)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_include_directive", True, True)
    app.add_config_value("readme_replace_attrs", True, True)
    app.add_config_value("readme_out_dir", Path(app.srcdir).parent.parent, True)
    app.add_config_value("linkcode_blob", 'head', True)

    app.setup_extension('sphinx.ext.linkcode')

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}


def resolve_readme(app: Sphinx, exception):
    rst_files = get_conf_val(app, "readme_src", [])
    out_dir = get_conf_val(app, "readme_out_dir")
    parse_include_directive = get_conf_val(app, "readme_include_directive")
    use_raw_directive = get_conf_val(app, "readme_raw_directive")
    docs_url = get_conf_val(app, "readme_docs_url", get_conf_val(app, "linkcode_url"))
    inline_markup = get_conf_val(app, "readme_inline_markup")
    link_type = get_conf_val(app, "readme_link_type")
    replace_attrs = get_conf_val(app, "readme_replace_attrs")

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
        rst, autodoc_refs = resolve_autodoc_refs(
            rst=rst_sources[rst_src],
            inline_markup=inline_markup,
            replace_attrs=replace_attrs,
            link_type=link_type
        )

        # Use ref_map to generate header for cross-refs in the file
        header_vals = get_header_vals(autodoc_refs, ref_map, inline_markup, link_type)

        rst = replace_rst_images(
            src_dir=app.srcdir,
            out_dir=out_dir,
            rst_src=rst_src,
            rst=rst
        )

        for role in ('ref', 'doc'):
            rst = replace_cross_refs(rst, ref_map, role)

        # Write the final output
        rst_out = os.path.join(
            out_dir, os.path.basename(rst_src)
        )
        with open(rst_out, 'w', encoding='utf-8') as f:
            f.write(
                "\n".join(header_vals) + "\n\n" + rst
            )
        print(
            f'``sphinx_readme``: saved generated .rst file to {rst_out}')


def replace_cross_refs(rst, ref_map, ref_role: str):
    # Find all :ref_role:`ref_id` cross-refs
    cross_refs = re.findall(
        pattern=fr":{ref_role}:`(.+)`",
        string=rst
    )
    # Match these ids up with target data in the ref_map
    cross_ref_map = dict(zip(cross_refs, ref_map[ref_role]))

    # Replace cross-refs with `text <link>`_ format
    for ref_id, target in cross_ref_map.items():
        rst = re.sub(
            pattern=rf":{ref_role}:`{ref_id}`",
            repl=rf"`{target['text']} <{target['refuri']}>`_",
            string=rst
        )
    return rst




def resolve_autodoc_refs(rst: str, inline_markup: bool, replace_attrs: bool, link_type: str):
    """
    :param rst:
    :param inline_markup:
    :param replace_attrs:
    :param link_type:
    :return:
    """
    # The rst could have :role:`{~.}{module|class}{.}target` where {} is optional
    # Roles to link to source code -> class, meth, func
    pattern = r":(?:class|meth|func):`([~\.\w]+)`"

    if replace_attrs:
        if link_type == 'code':
            # Links to source code aren't generated for properties/attributes
            # Replace :attr:`~.attribute` with ``attribute``
            rst = replace_autodoc_attrs(rst)

        else:
            # We can generate links to html documentation though!
            pattern = r":(?:class|meth|func|attr):`([~\.\w]+)`"

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
    return rst, autodoc_refs


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
    pattern = r"\W*?(.. admonition:: .*\n(?:\W+:class: \w+\n)?\n\W+.+\n\n+)+\S*"
    if raw_directive:
        admonition = '''
.. raw:: html

   <table>
      <tr align="left">
         <th>

{icon} {title}

.. raw:: html
    
    </th></tr>
    <tr><td>

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

