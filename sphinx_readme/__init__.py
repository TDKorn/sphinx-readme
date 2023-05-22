import sphinx
from pathlib import Path
from typing import Dict, Any
from docutils.nodes import Node
from sphinx.application import Sphinx
from sphinx_readme.utils import get_conf_val, set_conf_val
from sphinx_readme.parser import READMEParser


__version__ = "v0.0.1"


def setup(app: Sphinx) -> Dict[str, Any]:
    app.connect('doctree-resolved', parse_references)
    app.connect('build-finished', resolve_readme)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_include_directive", True, True)
    app.add_config_value("readme_replace_attrs", True, True)
    app.add_config_value("readme_out_dir", Path(app.srcdir).parent.parent, True)
    app.add_config_value("readme_linkcode_blob", 'head', True)
    app.add_config_value("readme_default_admonition_icon", "ℹ", True)

    set_conf_val(app, 'READMEParser', READMEParser(app))

    app.setup_extension('sphinx.ext.linkcode')

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}


def parse_references(app: Sphinx, doctree: Node, docname: str):
    readme = get_conf_val(app, 'READMEParser')
    readme.parse(doctree, docname)


def resolve_readme(app: Sphinx, exception):
    readme = get_conf_val(app, 'READMEParser')
    readme.resolve()
