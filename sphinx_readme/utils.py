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



def get_header_vals(refs: Dict[str, Dict[str, str]], inline_markup: bool = True) -> List[str]:
    header = []
    for ref in refs:
        link = refs[ref].get("link")
        target = refs[ref]['target']
        header.extend([
            f".. |.`{ref}`| replace:: ``{target}``",
            f".. |.{ref}| replace:: {target}"
        ])
        if link:
            header.append(".. _." + ref + ": " + link)
    return header

    # if inline_markup:
    #     sub = f".. |.`{ref}`| replace:: ``{target}``"
    # else:
    #     sub = f".. |.{ref}| replace:: {target}",


def write_header(header: List[str]):
    with open("sphinx-readme.rst", 'w', encoding="utf-8") as f:
        for line in header:
            f.write(line + "\n")
        f.write("\n\n")
