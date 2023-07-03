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
