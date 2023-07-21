------------------------
Extension Configuration
------------------------

Install using pip::

   pip install sphinx-readme


Add the extension to your ``conf.py``:


.. code-block:: python

   extensions = [
      "sphinx_readme",
   ]


For an example of the minimum required configuration,
please see the |sample-conf|_

.. _sample-conf: sample_conf.html
.. |sample-conf| replace:: sample ``conf.py`` file


.. _mandatory_vals:

Mandatory ``conf.py`` values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

``html_context``
======================

.. confval:: html_context

   A dictionary containing info about your repository (:external+sphinx:confval:`html_context`)

   * At minimum, the username and repository name must be specified
   * Please see `HTML Context Settings <https://docs.readthedocs.io/en/stable/guides/edit-source-links-sphinx.html>`_
     to determine the correct dictionary keys for your hosting platform

   :type: ``Dict``

``html_baseurl``
======================

.. confval:: html_baseurl

   The base URL which points to the root of the HTML documentation (:external+sphinx:confval:`html_baseurl`)

   :type: ``str``

``readme_src_files``
======================

.. confval:: readme_src_files

   An individual or list of ``rst`` files to parse

   .. important:: Filepaths should be specified relative to the source directory

   :type: ``Union[str, List]``

``readme_docs_url_type``
=========================

.. confval:: readme_docs_url_type

   The documentation source to link to when resolving :mod:`~.sphinx.ext.autodoc` cross-references

   Must be either ``"code"`` or ``"html"``

   * ``"code"``: uses :mod:`sphinx.ext.linkcode` to replace references with links to highlighted source code

    :Example:
       |parse_intersphinx_nodes|_

   * ``"html"``: replaces references with links to HTML documentation entries

    :Example:
       :meth:`~.parse_intersphinx_nodes`

   .. note::

      If set to ``code``, then :code:`:attr:` cross-references will not be replaced with links

      * Instead, they'll be replaced with ``inline literals`` or left as is
      * Please see :confval:`readme_replace_attrs` and :confval:`readme_inline_markup`


.. |parse_intersphinx_nodes| replace:: ``parse_intersphinx_nodes()``
.. _parse_intersphinx_nodes: https://github.com/TDKorn/sphinx-readme/blob/606f57b723e9d08deba9fda352b571a8594d7052/sphinx_readme/parser.py#L205-L229


.. _optional_vals:

Optional ``conf.py`` values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |rst_icon_map| replace:: :rst:`:attr:\`icon_map\``
.. |.`icon_map`| replace:: ``icon_map``
.. _.`icon_map`: https://sphinx-readme.readthedocs.io/en/latest/readme_config.html#sphinx_readme.config.main.READMEConfig.icon_map
.. |.icon_map| replace:: icon_map
.. _.icon_map: https://sphinx-readme.readthedocs.io/en/latest/readme_config.html#sphinx_readme.config.main.READMEConfig.icon_map

.. |rst_parse_autodoc_nodes| replace:: :rst:`:meth:\`parse_autodoc_nodes\``
.. |.`parse_autodoc_nodes`| replace:: ``parse_autodoc_nodes()``
.. _.`parse_autodoc_nodes`: https://sphinx-readme.readthedocs.io/en/latest/parser.html#sphinx_readme.parser.READMEParser.parse_autodoc_nodes
.. |.parse_autodoc_nodes| replace:: parse_autodoc_nodes()
.. _.parse_autodoc_nodes: https://sphinx-readme.readthedocs.io/en/latest/parser.html#sphinx_readme.parser.READMEParser.parse_autodoc_nodes



``readme_out_dir``
===================

.. confval:: readme_out_dir

  Specifies the path of the directory to save generated ``rst`` files to

  The value should be provided as either

  1. An absolute path; or
  2. A path relative to the source directory

  :type: *Union[str, Path]*
  :default: the root directory of your repository, via :func:`~.get_repo_dir`

``readme_replace_attrs``
========================

.. confval:: readme_replace_attrs

   Specifies if cross-references for attributes (``:attr:``) should be replaced

   ...

   If ``True``, the value of :confval:`readme_docs_url_type` determines how replacements are made:

   * ``"html"``: references are replaced with a link to the corresponding documentation entry

    :Example:
       |rst_icon_map| would be replaced with |.`icon_map`|_ or |.icon_map|_,
       depending on the value of :confval:`readme_inline_markup`

   * ``"code"``: attributes are replaced with inline markup

    :Example:
       |rst_icon_map| would be replaced with ``icon_map``


   :type: *bool*
   :default: ``True``

``readme_inline_markup``
========================

.. confval:: readme_inline_markup

   Specifies if replacements for autodoc cross-references should use inline markup

   * If ``True``, the substitution for |rst_parse_autodoc_nodes| would be |.`parse_autodoc_nodes`|_
   * If ``False``, the substitution for |rst_parse_autodoc_nodes| would be |.parse_autodoc_nodes|_

   :type: *bool*
   :default: ``True``

``readme_raw_directive``
=========================

.. confval:: readme_raw_directive

   Specifies if the ``raw`` directive is supported by the platform
   you intend to render the generated file on

   .. tip::

      * GitHub supports the ``raw`` directive
      * PyPi, GitLab, and BitBucket do not support the ``raw`` directive

   If set to ``False``,

   * Admonitions will be replaced with the ``csv-table`` directive instead of HTML tables
   * All ``raw`` directives in the file will be removed

   :type: *bool*
   :default: ``True``

``readme_include_directive``
=============================

.. confval:: readme_include_directive

   Specifies if ``include`` directives should be parsed
   (file content inserted) or removed

   :type: *bool*
   :default: ``True``

``readme_admonition_icons``
============================

.. confval:: readme_admonition_icons

   An optional mapping of admonition classes and their icons

   * If specified, will be used to update the :attr:`~.icon_map` (below)

   :type: *Optional[Dict[str, str]]*
   :default:

.. code-block:: python

    {
     'attention': '🔔️',
     'caution': '⚠️',
     'danger': '☢',
     'error': '⛔',
     'hint': '🧠',
     'important': '📢',
     'note': '📝',
     'tip': '💡',
     'warning': '🚩',
     'default': '📄'
    }

``readme_default_admonition_icon``
=====================================

.. confval:: readme_default_admonition_icon

   The icon to use when a generic admonition either

   * Has no class
   * Uses a class that has no corresponding icon in the :attr:`~.icon_map`

   :type: *str*
   :default: ``"📄"``

``readme_rubric_heading``
==========================

.. confval:: readme_rubric_heading

   The character to use when replacing rubrics with section headers

   Must be one of the following valid section title adornment characters::

       ! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~

   If not specified, rubrics will be replaced with bold text instead of a heading

   :type: *str*
   :default: bold inline markup (``**title**``)


``readme_blob``
================

.. confval:: readme_blob

   The repository blob to link to - any of ``"head"``, ``"last_tag"``, or ``"{blob}"``

   * ``"head"``: links to the most recent commit hash; if this commit is tagged, uses the tag instead
   * ``"last_tag"``: links to the most recently tagged commit; if no tags exist, uses ``"head"``
   * ``"{blob}"``: links to the specified blob, for example ``"master"`` or ``"v2.0.1"``

   :type: *str*
   :default: ``"head"``


``linkcode_resolve``
========================

.. confval:: linkcode_resolve

   A ``linkcode_resolve()`` function for :mod:`sphinx.ext.linkcode` to use
   when resolving the target of :mod:`~sphinx.ext.autodoc` cross-references

   :type: *Callable*
   :default: return value of :func:`~.get_linkcode_resolve`
