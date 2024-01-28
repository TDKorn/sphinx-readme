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
    'requests': ('https://requests.readthedocs.io/en/latest/', None),
    'sphinx': ('https://www.sphinx-doc.org/en/master/', None),
}
master_doc = 'index'
html_baseurl = 'https://sphinx-readme-testing.readthedocs.io/en/latest'
html_context = {
    'display_github': True,
    'github_user': 'TDKorn',
    'github_repo': 'sphinx-readme',
}
readme_out_dir = os.path.abspath('../output/')
