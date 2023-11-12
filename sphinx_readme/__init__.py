import os
import sphinx
from typing import Dict, Any
from docutils.nodes import document
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment

from sphinx_readme.utils.sphinx import get_conf_val, set_conf_val
from sphinx_readme.utils.git import get_repo_dir
from sphinx_readme.parser import READMEParser


__version__ = "v0.2.5"


def setup(app: Sphinx) -> Dict[str, Any]:
    # Avoid setting up extension if building on ReadTheDocs
    if os.environ.get("READTHEDOCS") == "True":
        return {}

    app.connect('env-check-consistency', parse_env)
    app.connect('doctree-resolved', parse_doctree)
    app.connect('build-finished', resolve)

    app.add_config_value("readme_inline_markup", True, True)
    app.add_config_value("readme_raw_directive", True, True)
    app.add_config_value("readme_include_directive", True, True)
    app.add_config_value("readme_replace_attrs", True, True)
    app.add_config_value("readme_out_dir", get_repo_dir(), True)
    app.add_config_value("readme_default_admonition_icon", "📄", True)
    app.add_config_value("readme_tags", ["readme"], True, list)
    app.add_config_value("readme_blob", 'head', True)

    set_conf_val(app, 'READMEParser', READMEParser(app))

    return {'version': sphinx.__display_version__, 'parallel_read_safe': True}


def parse_env(app: Sphinx, env: BuildEnvironment):
    parser = get_conf_val(app, 'READMEParser')
    parser.parse_env(env)


def parse_doctree(app: Sphinx, doctree: document, docname: str):
    parser = get_conf_val(app, 'READMEParser')
    parser.parse_doctree(app, doctree, docname)


def resolve(app: Sphinx, exception):
    parser = get_conf_val(app, 'READMEParser')
    parser.resolve()
