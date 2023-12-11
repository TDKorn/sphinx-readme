import os

readme_docs_url_type = "code"
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
html_baseurl = 'https://sphinx-readme.readthedocs.io/en/latest'
html_context = {
    'display_github': True,
    'github_user': 'TDKorn',
    'github_repo': 'sphinx-readme',
}
readme_out_dir = os.path.abspath('../output/')
