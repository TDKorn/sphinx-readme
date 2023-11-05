import re
from typing import List, Optional, Tuple
import sphinx.util.tags


def escape_rst(rst: str) -> str:
    """Escape regex special characters from the content of an ``rst`` file"""
    for char in ".+?*|()<>{}^$[]":
        rst = rst.replace(char, rf"\{char}")
    return rst


#: Characters that are allowed directly before a cross-reference
BEFORE_XREF = re.escape(":[{(/\"'-")
#: Characters that are allowed directly after a cross-reference
AFTER_XREF = re.escape(":;!?,\"'/\\])}-")


def format_hyperlink(target: str, text: str, sub_override: Optional[str] = None) -> Tuple[str, List[Optional[str]]]:
    """Formats a hyperlink, preserving any ``inline literals`` within the text

    Since nested inline markup isn't possible, substitutions are used
    when link text contains inline literals

    **Example:**

    >>> target = "https://www.github.com/tdkorn/sphinx-readme"
    >>> format_hyperlink(target, "The Sphinx README Repository")
    ('`The Sphinx README Repository <https://www.github.com/tdkorn/sphinx-readme>`_', [])

    >>> format_hyperlink(target, "The ``Sphinx README`` Repository") # doctest: +NORMALIZE_WHITESPACE
    ('|The Sphinx README Repository|_',
    ['.. |The Sphinx README Repository| replace:: The ``Sphinx README`` Repository',
     '.. _The Sphinx README Repository: https://www.github.com/tdkorn/sphinx-readme'])

    >>> format_hyperlink(target, "The ``Sphinx README`` Repository", sub_override="repo") # doctest: +NORMALIZE_WHITESPACE
    ('|repo|_',
    ['.. |repo| replace:: The ``Sphinx README`` Repository',
     '.. _repo: https://www.github.com/tdkorn/sphinx-readme'])

    :param target: the link URL
    :param text: the link text
    :param sub_override: overrides the name for the label/substitution, if applicable
    :returns: a tuple containing the formatted hyperlink and a list of substitution definitions
    """
    substitutions = []

    if "`" in text:
        # Substitutions must be used for inline literals
        sub = sub_override or text.replace('`', '')
        substitutions.extend([
            f".. |{sub}| replace:: {text}",
            f".. _{sub}: {target}"
        ])
        link = f"|{sub}|_"
    else:
        # Use a normal link otherwise
        link = f"`{text} <{target}>`_"

    return link, substitutions


def format_rst(inline_markup: str, rst: str, replace_attributes: bool = False) -> str:
    """Formats text with the specified type of inline markup

    Preserves any ``inline literals``, ``|substitutions|``, and
    :rst:`\`Custom Link Text <https://website.com>\`_` within the text

    **Example:**

    >>> format_rst("bold", "This is part of the ``sphinx_readme.utils`` module")
    "**This is part of the** ``sphinx_readme.utils`` **module**"


    **This is part of the** ``sphinx_readme.utils`` **module**

    :param inline_markup: either "bold" or "italic"
    :param rst: the rst content to format
    """
    if inline_markup == "bold":
        markup = "**"
    elif inline_markup == "italic":
        markup = "*"
    else:
        raise ValueError("``inline_markup`` must be either 'bold' or 'italic'")

    if replace_attributes:
        rst = replace_attrs(rst)

    split = re.split(r"\s*?(``.+?``|\|.+?\|_?|`.+? <.+?>`_)\s*?", rst)
    parts = []

    for part in split:
        if not part:
            continue
        if part.startswith("`") or part.startswith("|"):
            parts.append(part)
        else:
            parts.append(f"{markup}{part.strip()}{markup}")

    return " ".join(parts)


def replace_only_directives(rst: str, tags: sphinx.util.tags.Tags) -> str:
    """Replaces and removes :rst:dir:`only` directives.

    The :confval:`readme_tags` are temporarily added as :external+sphinx:ref:`tags <conf-tags>`,
    then the ``<expression>`` argument of the directive is evaluated.

    * If ``True``, the content will be used
    * If ``False``, the directive is removed

    .. tip:: The default value of :confval:`readme_tags` is ``["readme"]``


    **Expression Examples:**

    Using default value of :rst:`readme_tags = ["readme"]`:

    .. code-block:: rst

       .. only:: readme

          This will be included in the generated file

       .. only:: html

          This will be excluded from the generated file

       .. only:: readme or html

          This will be included in the generated file

       .. only:: readme and html

          This will be excluded from the generated file.

    Setting :rst:`readme_tags = ["pypi"]` in ``conf.py``:

    .. code-block:: rst

       .. only:: pypi

          This will be included in the generated file

       .. only:: readme

          This will be excluded from the generated file

       .. only:: readme or pypi

          This will be included in the generated file


    :param rst: the content of an ``rst`` file
    :param tags: the :class:`sphinx.util.tags.Tags` object
    """
    # Match all ``only`` directives
    pattern = r"\.\. only::\s+(\S.*?)\n+?((?:^[ ]+.+?$|^\s*$)+?)(?=\n*\S+|\Z)"
    directives = re.findall(pattern, rst, re.M | re.DOTALL)

    for expression, content in directives:
        # Pattern to match each block exactly
        pattern = rf"\.\. only:: {expression}\n+?{escape_rst(content)}\n*?"

        if tags.eval_condition(expression):
            # For replacement, remove preceding indent (3 spaces) from each line
            content = '\n'.join(line[3:] for line in content.split('\n'))

            # Replace directive with content
            rst = re.sub(pattern, rf"{content}", rst)

        else:
            # Remove directive
            rst = re.sub(pattern, '', rst)

    return rst


def remove_raw_directives(rst: str) -> str:
    """Removes all ``raw`` directives from ``rst``

    :param rst: the rst to remove ``raw`` directives from
    """
    return re.sub(
        pattern=r"(\.\. raw::\s+\S.*?\n+?(?:^[ ]+.+?$|^\s*$)+?)(?=\n*\S+|\Z)",
        repl='', string=rst, flags=re.M | re.DOTALL
    )


def replace_attrs(rst: str) -> str:
    """Replaces ``:attr:`` cross-references with ``inline literals``

    .. hint::

       Since source code links can't be generated for attributes,
       this function is only called if both

       1. :confval:`readme_docs_url_type` is ``"code"``
       2. :confval:`readme_replace_attrs` is ``True``

    :param rst: the rst to replace attribute xrefs in
    """
    # Ex. :attr:`~.Class.attr` => ``attr``
    short_ref = rf"(?<![^\s{BEFORE_XREF}])(?::py)?:attr:`~[.\w]*?([\w]+)`(?=[\s{AFTER_XREF}]|\Z)"
    # Ex. :attr:`.Class.attr` => ``Class.attr``
    long_ref = rf"(?<![^\s{BEFORE_XREF}])(?::py)?:attr:`\.?([.\w]+)`(?=[\s{AFTER_XREF}]|\Z)"
    repl = r"``\1``"

    rst = re.sub(short_ref, repl, rst)
    rst = re.sub(long_ref, repl, rst)
    return rst


def get_xref_variants(target: str) -> List[str]:
    """Returns a list of ways to make a cross-reference to ``target``

    **Example:**

    >>> get_xref_variants('mod.Class.meth')
    ['mod.Class.meth', '.mod.Class.meth', '~mod.Class.meth', '~.mod.Class.meth']

    :param target: the object to generate cross-reference syntax for
    """
    return [prefix + target for prefix in ('', '.', '~', '~.')]


def get_all_xref_variants(fully_qualified_name: str) -> List[str]:
    """Returns all possible cross-reference targets for an object

    **Example:**

    >>> get_all_xref_variants("sphinx_readme.utils.get_all_xref_variants") # doctest: +NORMALIZE_WHITESPACE
    ['get_all_xref_variants', '.get_all_xref_variants', '~get_all_xref_variants',
    '~.get_all_xref_variants', 'utils.get_all_xref_variants', '.utils.get_all_xref_variants',
    '~utils.get_all_xref_variants', '~.utils.get_all_xref_variants',
    'sphinx_readme.utils.get_all_xref_variants', '.sphinx_readme.utils.get_all_xref_variants',
    '~sphinx_readme.utils.get_all_xref_variants', '~.sphinx_readme.utils.get_all_xref_variants']

    :param fully_qualified_name: the fully qualified name of the target (ex. ``pkg.module.class.method``)
    """
    parts = fully_qualified_name.split(".")[::-1]  # => ['meth', 'Class', 'mod', "pkg"]
    variants = []

    for i, part in enumerate(parts):
        target = '.'.join(parts[i::-1])  # 'meth', 'Class.meth', 'mod.class.meth', 'pkg.mod.class.meth'
        variants.extend(get_xref_variants(target))

    return variants
