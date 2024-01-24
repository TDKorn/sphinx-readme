from setuptools import setup, find_packages

setup(
    name="sphinx-readme-test-package",
    version='1.0.0',
    description="Test Package for Sphinx README",
    long_description="Test Package for Sphinx README",
    long_description_content_type="text/x-rst",
    author="Adam Korn",
    author_email='hello@dailykitten.net',
    license="MIT License",
    packages=find_packages(),
    url="https://github.com/tdkorn/sphinx-readme/blob/main/tests",
    install_requires=["sphinx==5.3.0","docutils<0.17"],
)
