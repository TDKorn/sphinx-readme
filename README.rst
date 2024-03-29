.. |.configuration/configuring| replace:: Extension Configuration
.. _.configuration/configuring: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html
.. |.html_baseurl| replace:: ``html_baseurl``
.. _.html_baseurl: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-html_baseurl
.. |.html_context| replace:: ``html_context``
.. _.html_context: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-html_context
.. |.~.parse_intersphinx_nodes| replace:: ``parse_intersphinx_nodes()``
.. _.~.parse_intersphinx_nodes: https://github.com/TDKorn/sphinx-readme/blob/v1.2.1/sphinx_readme/parser.py#L256-L293
.. |.read the docs user documentation+guides/edit-source-links-sphinx-colon-github+HTML Context Settings| replace:: HTML Context Settings
.. _.read the docs user documentation+guides/edit-source-links-sphinx-colon-github+HTML Context Settings: https://docs.readthedocs.io/en/stable/guides/edit-source-links-sphinx.html#github
.. |.readme_docs_url_type| replace:: ``readme_docs_url_type``
.. _.readme_docs_url_type: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_docs_url_type
.. |.readme_inline_markup| replace:: ``readme_inline_markup``
.. _.readme_inline_markup: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_inline_markup
.. |.readme_out_dir+output directory| replace:: ``output directory``
.. _.readme_out_dir+output directory: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_out_dir
.. |.readme_raw_directive| replace:: ``readme_raw_directive``
.. _.readme_raw_directive: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_raw_directive
.. |.readme_replace_attrs| replace:: ``readme_replace_attrs``
.. _.readme_replace_attrs: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_replace_attrs
.. |.readme_src_files| replace:: ``readme_src_files``
.. _.readme_src_files: https://sphinx-readme.readthedocs.io/en/latest/configuration/configuring.html#confval-readme_src_files
.. |.sphinx+html_baseurl| replace:: ``html_baseurl``
.. _.sphinx+html_baseurl: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_baseurl
.. |.sphinx+html_context| replace:: ``html_context``
.. _.sphinx+html_context: https://www.sphinx-doc.org/en/master/usage/configuration.html#confval-html_context
.. |.sphinx+usage/domains/restructuredtext+reStructuredText Domain| replace:: reStructuredText Domain
.. _.sphinx+usage/domains/restructuredtext+reStructuredText Domain: https://www.sphinx-doc.org/en/master/usage/domains/restructuredtext.html
.. |.sphinx+usage/domains/standard+Standard Domain| replace:: Standard Domain
.. _.sphinx+usage/domains/standard+Standard Domain: https://www.sphinx-doc.org/en/master/usage/domains/standard.html
.. |.~.sphinx.domains.python.PythonDomain| replace:: ``PythonDomain``
.. _.~.sphinx.domains.python.PythonDomain: https://www.sphinx-doc.org/en/master/extdev/domainapi.html#sphinx.domains.python.PythonDomain
.. |.~.sphinx.environment.BuildEnvironment| replace:: ``BuildEnvironment``
.. _.~.sphinx.environment.BuildEnvironment: https://www.sphinx-doc.org/en/master/extdev/envapi.html#sphinx.environment.BuildEnvironment
.. |.sphinx.ext.autodoc| replace:: ``sphinx.ext.autodoc``
.. _.sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
.. |.~.sphinx.ext.autodoc| replace:: ``autodoc``
.. _.~.sphinx.ext.autodoc: https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#module-sphinx.ext.autodoc
.. |.sphinx.ext.linkcode| replace:: ``sphinx.ext.linkcode``
.. _.sphinx.ext.linkcode: https://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html#module-sphinx.ext.linkcode



.. role:: rst(code)
   :class: highlight

.. |env| replace:: |.~.sphinx.environment.BuildEnvironment|_
.. |py_domain| replace:: |.~.sphinx.domains.python.PythonDomain|_
.. |std_domain| replace:: |.sphinx+usage/domains/standard+Standard Domain|_
.. |rst_domain| replace:: |.sphinx+usage/domains/restructuredtext+reStructuredText Domain|_

.. meta::
   :author: Adam Korn
   :title: Sphinx README - Generate README.rst That Renders Beautifully on GitHub, PyPi, GitLab, BitBucket
   :description: Sphinx extension to generate reStructuredText README.rst files that render beautifully on GitHub, PyPi, GitLab, BitBucket



.. raw:: html

   <div align="center">

.. image:: https://raw.githubusercontent.com/TDKorn/sphinx-readme/v1.2.1/docs/source/_static/logo_readme.png
   :alt: Sphinx README: Generate Beautiful reStructuredText README.rst for GitHub, PyPi, GitLab, BitBucket
   :align: center
   :width: 25%



.. raw:: html

   <h1>Sphinx README</h1>





A Sphinx extension to generate ``README.rst`` files that render beautifully on GitHub, PyPi, GitLab, BitBucket

.. |RTD| replace:: **Explore the docs »**
.. _RTD: https://sphinx-readme.readthedocs.io/en/latest/

|RTD|_



.. image:: https://img.shields.io/pypi/v/sphinx-readme?color=eb5202
   :target: https://pypi.org/project/sphinx-readme
   :alt: PyPI Project for Sphinx README: Generate Beautiful reStructuredText README.rst for GitHub, PyPi, GitLab, BitBucket

.. image:: https://img.shields.io/badge/GitHub-sphinx--readme-4f1abc
   :target: https://github.com/tdkorn/sphinx-readme
   :alt: GitHub Repository for Sphinx README: Generate Beautiful reStructuredText README.rst for GitHub, PyPi, GitLab, BitBucket

.. image:: https://static.pepy.tech/personalized-badge/sphinx-readme?period=total&units=none&left_color=grey&right_color=blue&left_text=Downloads
   :target: https://pepy.tech/project/sphinx-readme
   :alt: Downloads for Sphinx README

.. image:: https://readthedocs.org/projects/sphinx-readme/badge/?version=latest
   :target: https://sphinx-readme.readthedocs.io/en/latest/?badge=latest
   :alt: Documentation for Sphinx README: Generate Beautiful reStructuredText README.rst for GitHub, PyPi, GitLab, BitBucket

.. image:: https://img.shields.io/github/actions/workflow/status/TDKorn/sphinx-readme/tests.yml?label=build&color=33ce57
   :target: https://github.com/TDKorn/sphinx-readme/actions/workflows/tests.yml
   :alt: Build Status

.. image:: https://codecov.io/gh/TDKorn/sphinx-readme/graph/badge.svg?token=RZCUCGIU0Q
   :target: https://codecov.io/gh/TDKorn/sphinx-readme
   :alt: Code Coverage

.. raw:: html

   </div>

|

About Sphinx README
~~~~~~~~~~~~~~~~~~~~~~~


.. raw:: html

   <table>
       <tr align="left">
           <th>

📚 What's Sphinx README?

.. raw:: html

   </th>
   <tr><td>

``sphinx_readme`` is a ``reStructuredText`` parser that uses Sphinx
to generate ``rst`` files that render beautifully on
GitHub, PyPi, GitLab, and BitBucket.

.. raw:: html

   </td></tr>
   </table>



**With** ``sphinx_readme`` **, there's no need to rewrite your** ``README.rst`` **as a** ``README.md`` **file**

Files generated by ``sphinx_readme`` have nearly identical appearance and functionality
as ``html`` builds, including |.sphinx.ext.autodoc|_ cross-references!



.. image:: https://raw.githubusercontent.com/TDKorn/sphinx-readme/v1.2.1/docs/source/_static/demo/demo.gif
   :alt: Demonstration of how reStructuredText README.rst files generated by Sphinx README render on GitHub, PyPi, GitLab, BitBucket
   :width: 75%


📋 Features
~~~~~~~~~~~~

``sphinx_readme`` adds support for the following ``sphinx`` and ``docutils`` directives and features:

* |.sphinx.ext.autodoc|_ cross-references (``:mod:``, ``:class:``, ``:meth:``, ``:func:``, and ``:attr:``)
* Standard cross-reference roles (``:doc:`` and ``:ref:``)
* Generic and Specific Admonitions
* Only directives
* Toctrees
* Rubrics
* Images


⚙ Installation
~~~~~~~~~~~~~~~~

Install using pip::

   pip install sphinx-readme


Add the extension to your ``conf.py``:

.. code-block:: python

   extensions = [
      'sphinx_readme',
   ]



🔧 Configuration
~~~~~~~~~~~~~~~~~




Please see |.configuration/configuring|_ for full documentation on configuration variables


Mandatory ``conf.py`` Values
==================================

|.html_context|_
 A dictionary containing info about your repository (|.sphinx+html_context|_)

  **Type:** ``dict``

 * At minimum, the username and repository name must be specified
 * Please see |.read the docs user documentation+guides/edit-source-links-sphinx-colon-github+HTML Context Settings|_
   to determine the correct dictionary keys for your hosting platform


|

|.html_baseurl|_
 The base URL which points to the root of the HTML documentation (|.sphinx+html_baseurl|_)

  **Type:** ``str``


|

|.readme_src_files|_
 An individual/list of ``rst`` source files to parse, or a dictionary of source files mapped to output files

  **Type:** ``Union[str, List[str], Dict[str,str]]``


.. raw:: html

   <table>
       <tr align="left">
           <th>

📢 Important

.. raw:: html

   </th>
   <tr><td>

Filepaths should be specified relative to the source directory
and |.readme_out_dir+output directory|_

.. raw:: html

   </td></tr>
   </table>


|

|.readme_docs_url_type|_
 The documentation source to link to when resolving |.~.sphinx.ext.autodoc|_ cross-references

  **Type:** ``str``

 Must be either ``"code"`` or ``"html"``

 * ``"code"``: uses |.sphinx.ext.linkcode|_ to replace references with links to highlighted source code

   **Example**: |.~.parse_intersphinx_nodes|_


 * ``"html"``: replaces references with links to HTML documentation entries

   **Example**: |parse_intersphinx_nodes_html|_


.. raw:: html

   <table>
       <tr align="left">
           <th>

📝 Note

.. raw:: html

   </th>
   <tr><td>

If set to ``code``, non-external :code:`:attr:` cross-references will not be replaced with links

* Instead, they'll be replaced with ``inline literals`` or left as is
* Please see |.readme_replace_attrs|_ and |.readme_inline_markup|_

.. raw:: html

   </td></tr>
   </table>



.. |parse_intersphinx_nodes_html| replace:: ``parse_intersphinx_nodes()``
.. _parse_intersphinx_nodes_html: http://sphinx-readme.readthedocs.io/en/latest/parser.html#sphinx_readme.parser.READMEParser.parse_intersphinx_nodes


Sample ``conf.py``
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

   extensions = [
      "sphinx_readme",
   ]

   html_context = {
      'display_github': True,
      'github_user': 'TDKorn',
      'github_repo': 'sphinx-readme',
   }

   html_baseurl = "https://sphinx-readme.readthedocs.io/en/latest"

   readme_src_files = "README.rst"

   readme_docs_url_type = "code"




.. raw:: html

   <table>
       <tr align="left">
           <th>

📢 Important

.. raw:: html

   </th>
   <tr><td>

For platforms that don't support the ``raw`` directive (PyPi, GitLab, and BitBucket),
be sure to disable |.readme_raw_directive|_:

.. code-block:: python

   readme_raw_directive = False

.. raw:: html

   </td></tr>
   </table>




📚 Documentation
~~~~~~~~~~~~~~~~

Full documentation can be found on |docs|_


.. |docs| replace:: ``ReadTheDocs``
.. _docs: https://sphinx-readme.readthedocs.io/en/latest

