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


def read_rst(rst_file: Union[str, Path], parse_include: bool = False):
    with open(rst_file, 'r', encoding='utf-8') as f:
        rst = f.read()

    if parse_include:
        # Find all included files
        included = re.findall(
            pattern=r"^\.\. include:: ([/\w]+\.rst)",
            string=rst,
            flags=re.M
        )
        for include in included:
            # Determine abs path of included file
            file = (Path(rst_file).parent / Path(include)).resolve()

            # Sub in the file content
            rst = re.sub(
                pattern=rf".. include:: {include}",
                repl=read_rst(file, parse_include),
                string=rst
            )
    else:
        # Remove all include directives from the text
        rst = re.sub(r"^\.\. include:: [/\w]+\.rst", '', rst, re.M)

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
