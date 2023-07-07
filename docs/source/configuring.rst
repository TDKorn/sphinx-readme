------------------------
Extension Configuration
------------------------

Install using pip::

   pip install sphinx-readme


Then add the extension to your ``conf.py``:

.. code-block:: python

   extensions = [
      "sphinx_readme",
   ]

...

.. _mandatory_vals:

.. include:: configuration/mandatory_config.rst


.. _optional_vals:

Optional ``conf.py`` values
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. |rst_icon_map| replace:: :rst:`:attr:\`icon_map\``
.. |.`icon_map`| replace:: ``icon_map``
.. _.`icon_map`: https://sphinx-readme.readthedocs.io/en/latest/config.html#sphinx_readme.config.main.READMEConfig.icon_map
.. |icon_map| replace:: icon_map
.. _icon_map: https://sphinx-readme.readthedocs.io/en/latest/config.html#sphinx_readme.config.main.READMEConfig.icon_map


``readme_out_dir``
===================

.. confval:: readme_out_dir

  Specifies the path of the directory to save generated ``rst`` files to

  The value should be provided as either

  1. An absolute path; or
  2. A path relative to the source directory

  :type: *str*
  :default: the root directory of your repository, via :func:`~.get_repo_dir`


.. confval:: readme_replace_attrs

   Specifies if attribute cross-refs (``:attr:``) should be replaced.

   If ``True``, the :confval:`readme_docs_url` determines how cross-refs will be replaced:

    **1.** If :confval:`readme_docs_url` links to html documentation, attributes are replaced
    by a link to the documentation stub

       * For example, |rst_icon_map| would be replaced by |.`icon_map`|_ or |icon_map|_,
         depending on the value of :confval:`readme_inline_markup`


    **2.** If :confval:`readme_docs_url` links to source code, attributes are replaced by inline markup only

       * For example, |rst_icon_map| would be replaced by ``icon_map``

   :type: *bool*
   :default: ``True``

.. confval:: readme_inline_markup

   Specifies if autodoc cross-ref substitutions should use inline markup

   * If ``True``, the substitution for |rst_icon_map| would be |.`icon_map`|_
   * If ``False``, the substitution for |rst_icon_map| would be |icon_map|_

   :type: bool
   :default: True

.. confval:: readme_raw_directive

   Specifies if the ``raw`` directive is supported by the platform
   you intend to render the generated file on

   .. tip::

      * GitHub supports the ``raw`` directive
      * PyPi and GitLab do not support the ``raw`` directive

   The ``raw`` directive is used to insert html tables as replacements for admonitions;
   if set to ``False``, the ``csv-table`` directive is used instead

   :type: bool
   :default: True


.. confval:: readme_include_directive

   Specifies if ``include`` directives should be parsed
   (file content inserted) or removed

   :type: bool
   :default: ``True``

.. confval:: readme_admonition_icons

   An optional mapping of admonition classes and their icons

   * If specified, will be used to update the :attr:`~.icon_map`

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

.. confval:: readme_default_admonition_icon

   The icon to use when a generic admonition either

   * Has no class
   * Uses a class that has no corresponding icon in the :attr:`~.icon_map`

   :type: *str*
   :default: ``📄``

.. confval:: readme_rubric_heading

   The character to use when replacing rubrics with section headers

   Must be one of the following valid section title adornment characters::

       ! " # $ % & ' ( ) * + , - . / : ; < = > ? @ [ \ ] ^ _ ` { | } ~

   If not specified, rubrics will be replaced with bold text instead of a heading

   :type: *str*
   :default: bold inline markup (``**title**``)


.. confval:: readme_blob

   The blob to link to on GitHub - any of ``"head"``, ``"last_tag"``, or ``"{blob}"``

   * ``head`` (default): links to the most recent commit hash; if this commit is tagged, uses the tag instead
   * ``last_tag``: links to the most recently tagged commit; if no tags exist, uses ``head``
   * ``blob``: links to any blob you want, for example ``"master"`` or ``"v2.0.1"``

   :type: *str*
   :default: ``"head"``

.. confval:: readme_linkcode_url

   The link to your GitHub repository formatted as ``https://github.com/user/repo``

   * If not specified, will attempt to create the link from the ``html_context`` dict

   :type: *str*
   :default: :code:`f"https://github.com/{html_context['github_user']}/{html_context['github_repo']}`


...

``linkcode_link_text``
========================

.. code-block:: python

   linkcode_link_text: str = "View on GitHub"


The text to use for the linkcode link

...

``linkcode_resolve``
========================

.. code-block:: python

   linkcode_resolve: types.FunctionType

A ``linkcode_resolve()`` function to use for resolving the link target

* Uses default function from |.get_linkcode_resolve|_ if not specified (recommended)

|