Mandatory ``conf.py`` values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. confval:: html_context

   A dictionary containing info about your repository (:external+sphinx:confval:`html_context`)

   * At minimum, the username and repository name must be specified
   * Please see `HTML Context Settings <https://docs.readthedocs.io/en/stable/guides/edit-source-links-sphinx.html>`_
     to determine the correct dictionary keys for your hosting platform

   :type: ``Dict``



.. confval:: html_baseurl

   The base URL which points to the root of the HTML documentation (:external+sphinx:confval:`html_baseurl`)

   :type: ``str``


.. confval:: readme_src_files

   An individual or list of ``rst`` files to parse

   .. important:: Filepaths should be specified relative to the source directory

   :type: ``Union[str, List]``


.. confval:: readme_docs_url_type

   The documentation source to link to when resolving :mod:`~.sphinx.ext.autodoc` cross-references

   Must be either ``"code"`` or ``"html"``

   * ``"code"``: uses :mod:`sphinx.ext.linkcode` to replace references with links to highlighted source code

     *Example*: |parse_intersphinx_node|_

   * ``"html"``: replaces references with links to HTML documentation entries

     *Example*: :meth:`~.parse_intersphinx_node`

   .. note::

      If set to ``code``, then :code:`:attr:` cross-references will not be replaced with links

      * Instead, they'll be replaced with ``inline literals`` or left as is
      * Please see :confval:`readme_replace_attrs` and :confval:`readme_inline_markup`


.. |parse_intersphinx_node| replace:: ``parse_intersphinx_node()``
.. _parse_intersphinx_node: https://github.com/TDKorn/sphinx-readme/blob/50c8f2b12d55c89caf68b525a757ed3e701576ff/sphinx_readme/parser.py#L78-L88

