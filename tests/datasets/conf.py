import os
import sys

sys.path.insert(0, os.path.abspath('../test_package'))

readme_docs_url_type = "code"
readme_blob = "main"
extensions = [
    'sphinx_readme',
    'sphinx.ext.autodoc',
    'sphinx.ext.intersphinx',
]
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'sphinx_readme': ('https://sphinx-readme.readthedocs.io/en/latest/', None),
}
master_doc = 'index'
html_baseurl = 'https://sphinx-readme-testing.readthedocs.io/en/latest'
html_context = {
    'display_github': True,
    'github_user': 'TDKorn',
    'github_repo': 'sphinx-readme',
}
html_theme = 'sphinx_rtd_theme'
readme_out_dir = os.path.abspath('../output/')


def setup(app):
    from sphinx.domains.python import PyField
    from sphinx.util.docfields import Field
    from sphinx.locale import _

    app.add_object_type(
        'confval',
        'confval',
        objname='configuration value',
        indextemplate='pair: %s; configuration value',
        doc_field_types=[
            PyField(
                'type',
                label=_('Type'),
                has_arg=False,
                names=('type',),
                bodyrolename='class'
            ),
            Field(
                'default',
                label=_('Default'),
                has_arg=False,
                names=('default',),
            ),
        ]
    )
