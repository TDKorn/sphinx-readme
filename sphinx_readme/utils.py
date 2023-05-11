import re
from sphinx.application import Sphinx
from typing import Dict, List, Optional, Any


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


def read_rst(rst_file: str, parse_include: bool = False):
    with open(rst_file, 'r', encoding='utf-8') as f:
        rst = f.read()
    if parse_include:
        rst = re.sub(
            pattern=r".. include:: ([/\w]+.rst)",
            repl=include_rst,
            string=rst
        )
    return rst


def include_rst(match):
    rst_file = match.group(1)
    return read_rst(rst_file)
