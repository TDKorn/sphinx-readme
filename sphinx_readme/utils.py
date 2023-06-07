import re
from pathlib import Path
from sphinx.application import Sphinx
from typing import Dict, List, Optional, Any, Union


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


def read_source_files(rst_files: Union[str, List], srcdir: str, parse_include: bool):
    if isinstance(rst_files, str):
        rst_files = [rst_files]

    rst_files = [
        # Absolute path of files; files should be relative to source directory
        str((Path(srcdir) / Path(rst_file)).resolve())
        for rst_file in rst_files
    ]
    # Create dict of {file: text} - all parsing is done on this text
    rst_sources = {
        rst_file: read_rst(str(rst_file), parse_include)
        for rst_file in rst_files
    }
    return rst_sources


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
