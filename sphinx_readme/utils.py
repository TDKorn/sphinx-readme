import re
import subprocess
from pathlib import Path
from sphinx.application import Sphinx
from typing import Dict, List, Optional, Any, Union
from sphinx.util import logging


logger = logging.getLogger(__name__)


def get_conf_val(app: Sphinx, attr: str, default: Optional[Any] = None) -> Any:
    """Retrieve the value of a ``conf.py`` config variable

    :param attr: the config variable to retrieve
    :param default: the default value to return if the variable isn't found
    """
    return app.config._raw_config.get(attr, getattr(app.config, attr, default))


def set_conf_val(app: Sphinx, attr: str, value: Any) -> None:
    """Set the value of a ``conf.py`` config variable

    :param attr: the config variable to set
    :param value: the variable value
    """
    app.config._raw_config[attr] = value
    setattr(app.config, attr, value)


def escape_rst(rst: str) -> str:
    """Escape regex special characters from the content of an ``rst`` file"""
    for char in ".+?*|()<>{}^$[]":
        rst = rst.replace(char, rf"\{char}")
    return rst


def format_rst(inline_markup: str, rst: str) -> str:
    """Formats text with the specified type of inline markup

    Preserves any ``inline literals`` within the text

    :Example::

        >>> format_rst("bold", "This is part of the ``sphinx_readme.utils`` module")
        "**This is part of the** ``sphinx_readme.utils`` **module**"

    :param inline_markup: either "bold" or "italic"
    :param rst: the rst content to format
    """
    if inline_markup == "bold":
        markup = "**"
    elif inline_markup == "italic":
        markup = "*"
    else:
        raise ValueError("``inline_markup`` must be either 'bold' or 'italic'")

    split = re.split(r"(?<=\S)(\s*?``.+?``\s*?)(?=\S)", rst)
    parts = []

    for part in split:
        if "`" in part:
            parts.append(part.strip())
        else:
            parts.append(f"{markup}{part}{markup}")

    return " ".join(parts)


def replace_only_directives(rst: str) -> str:
    """Replaces and removes ``only`` directives

    If ``"readme"`` is in the ``<expression>`` part of the
    ``only`` directive, the content will be used.

    Otherwise, the directive will be removed

    :param rst: the content of an ``rst`` file
    """
    # Match all ``only`` directives
    pattern = r"\.\. only::\s+(\S.*?)\n+?((?:^[ ]+.+?$|^\s*$)+?)(?=\n*\S+|\Z)"
    directives = re.findall(pattern, rst, re.M | re.DOTALL)

    for expression, content in directives:
        # Pattern to match each block exactly
        pattern = rf"\.\. only:: {expression}\n+?{escape_rst(content)}\n*?"

        if 'readme' in expression:
            # For replacement, remove preceding indent (3 spaces) from each line
            content = '\n'.join(line[3:] for line in content.split('\n'))

            # Replace directive with content
            rst = re.sub(pattern, rf"{content}", rst)

        else:
            # Remove directive
            rst = re.sub(pattern, '', rst)

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
