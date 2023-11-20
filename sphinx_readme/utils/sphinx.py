from typing import Any, Optional
from sphinx.application import Sphinx
from sphinx.util.logging import getLogger


logger = getLogger(__name__)


class ExternalRef:

    """Data structure to parse external cross-reference data from intersphinx"""
    def __init__(self, objtype: str, pkg: str, version: str, target: str, label: str, ref_id: str):
        self.objtype = objtype
        self.pkg = pkg
        self.id = ref_id
        self.label = label
        self.target = target
        self.version = version

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, ref_id):
        if not self.objtype.startswith("py"):
            # Include pkg to differentiate between local/external xrefs
            ref_id = f"{self.pkg.lower()}+{ref_id}"
        self._id = ref_id

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, label):
        if label == '-':
            label = self.id.split("+")[-1]
        self._label = label


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
