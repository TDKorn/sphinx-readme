from typing import Any, Optional
from sphinx.application import Sphinx
from sphinx.util.logging import getLogger


logger = getLogger(__name__)


def set_conf_val(app: Sphinx, attr: str, value: Any) -> None:
    """Set the value of a ``conf.py`` config variable

    :param attr: the config variable to set
    :param value: the variable value
    """
    app.config._raw_config[attr] = value
    setattr(app.config, attr, value)


def get_conf_val(app: Sphinx, attr: str, default: Optional[Any] = None) -> Any:
    """Retrieve the value of a ``conf.py`` config variable

    :param attr: the config variable to retrieve
    :param default: the default value to return if the variable isn't found
    """
    return app.config._raw_config.get(attr, getattr(app.config, attr, default))
