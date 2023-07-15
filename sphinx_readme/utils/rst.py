import re
from typing import List


def escape_rst(rst: str) -> str:
    """Escape regex special characters from the content of an ``rst`` file"""
    for char in ".+?*|()<>{}^$[]":
        rst = rst.replace(char, rf"\{char}")
    return rst


def format_rst(inline_markup: str, rst: str) -> str:
    """Formats text with the specified type of inline markup

    Preserves any ``inline literals`` within the text

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

    split = re.split(r"(?<=\S)(\s*?``.+?``\s*?)(?=\S)", rst)
    parts = []

    for part in split:
        if "`" in part:
            parts.append(part.strip())
        else:
            parts.append(f"{markup}{part}{markup}")

    return " ".join(parts)


def replace_only_directives(rst: str) -> str:
    """Replaces and removes :rst:dir:`only` directives.

    If ``"readme"`` is in the ``<expression>`` part of the
    directive, the content of the directive will be used.

    Otherwise, the directive will be removed.

    :param rst: the content of an ``rst`` file
    """
    # Match all ``only`` directives
    pattern = r"\.\. only::\s+(\S.*?)\n+?((?:^[ ]+.+?$|^\s*$)+?)(?=\n*\S+|\Z)"
    directives = re.findall(pattern, rst, re.M | re.DOTALL)

    for expression, content in directives:
        # Pattern to match each block exactly
        pattern = rf"\.\. only:: {expression}\n+?{escape_rst(content)}\n*?"

        if 'readme' in expression:
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
