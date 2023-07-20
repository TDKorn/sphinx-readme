from docutils import nodes
from docutils.core import publish_doctree
from sphinx.application import Sphinx


def get_doctree(app: Sphinx, rst: str, docname: str = 'index') -> nodes.document:
    """Generate doctree from a string of reStructuredText using Sphinx application."""
    try:
        app.env.temp_data['docname'] = docname
        return publish_doctree(rst, settings_overrides={
            'env': app.env,
            'gettext_compact': True,
            "report_level": 4,
            "halt_level": 5
        })
    finally:
        app.env.temp_data.pop('docname', None)
