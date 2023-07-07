import os
from setuptools import setup, find_packages

LONG_DESCRIPTION_SRC = 'README.rst'


def read(file):
    with open(os.path.abspath(file), 'r', encoding='utf-8') as f:
        return f.read()


def get_version():
    file = os.path.abspath(os.path.join('sphinx_readme', '__init__.py'))
    for line in read(file).split('\n'):
        if line.startswith("__version__ ="):
            return line.split(" = ")[-1].strip('"')


setup(
    name="sphinx-readme",
    version=get_version(),
    description="Generate Beautiful reStructuredText README.rst for GitHub, PyPi, GitLab, BitBucket",
    long_description=read(LONG_DESCRIPTION_SRC),
    long_description_content_type="text/x-rst; charset=UTF-8",
    author="Adam Korn",
    author_email='hello@dailykitten.net',
    license="MIT License",
    packages=find_packages(),
    keywords=[
        "sphinx", "docutils", "sphinx-extension", "sphinx-contrib", "reStructuredText", "rst",
        "reST", "parser", "rst-parser", "README.rst", "README", "autodoc", "linkcode"
    ],
    url="https://github.com/tdkorn/sphinx-readme",
    download_url="https://github.com/TDKorn/sphinx-readme/tarball/main",
    classifiers=[
        "Framework :: Sphinx :: Extension",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
    ],
    install_requires=["sphinx>=1.8"],
)
