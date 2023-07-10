import os
import sphinx
from typing import Dict, Any
from docutils.nodes import document
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx_readme.utils import get_conf_val, set_conf_val
from sphinx_readme.config import get_repo_dir
from sphinx_readme.parser import READMEParser


__version__ = "v0.0.1b6"


def setup(app: Sphinx) -> Dict[str, Any]:
    # Avoid setting up extension if building on ReadTheDocs
    if os.environ.get("READTHEDOCS") == "True":
        return {}

    app.connect('env-check-consistency', parse_titles)
    app.connect('doctree-resolved', parse_references)
    app.connect('build-finished', resolve_readme)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_include_directive", True, True)
    app.add_config_value("readme_replace_attrs", True, True)
    app.add_config_value("readme_out_dir", get_repo_dir(), True)
    app.add_config_value("readme_blob", 'head', True)
    app.add_config_value("readme_default_admonition_icon", "📄", True)

    set_conf_val(app, 'READMEParser', READMEParser(app))

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}

def parse_titles(app: Sphinx, env: BuildEnvironment):
    readme = get_conf_val(app, 'READMEParser')
    readme.parse_titles(env)


def parse_references(app: Sphinx, doctree: document, docname: str):
    readme = get_conf_val(app, 'READMEParser')
    readme.parse(app, doctree, docname)


def resolve_readme(app: Sphinx, exception):
    readme = get_conf_val(app, 'READMEParser')
    readme.resolve()
