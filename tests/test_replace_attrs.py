import pytest
from sphinx_readme.utils.rst import replace_attrs, get_all_xref_variants

target = "Class.attribute"
variants = get_all_xref_variants(target)
short_refs, long_refs = [], []

for variant in variants:
    if variant.startswith("~"):
        short_refs.append(f":attr:`{variant}`")
    else:
        long_refs.append(f":attr:`{variant}`")

inputs_wrong = [
    *[(ref, "``attribute``") for ref in short_refs],
    *[(f":py{ref}", "``attribute``") for ref in short_refs],
    *[(ref, "``Class.attribute``") for ref in short_refs],
    *[(f":py{ref}", "``Class.attribute``") for ref in short_refs]
]


@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        # Short refs
        (":attr:`~attribute`", '``attribute``'),
        (":attr:`~.attribute`", '``attribute``'),
        (":attr:`~.Class.attribute`", '``attribute``'),
        (":attr:`~Class.attribute`", '``attribute``'),
        (":py:attr:`~attribute`", '``attribute``'),
        (":py:attr:`~.attribute`", '``attribute``'),
        (":py:attr:`~.Class.attribute`", '``attribute``'),
        (":py:attr:`~Class.attribute`", '``attribute``'),
        # Long Refs
        (":attr:`attribute`", '``attribute``'),
        (":attr:`.attribute`", '``attribute``'),
        (":attr:`.Class.attribute`", '``Class.attribute``'),
        (":attr:`Class.attribute`", '``Class.attribute``'),
        (":py:attr:`attribute`", '``attribute``'),
        (":py:attr:`.attribute`", '``attribute``'),
        (":py:attr:`.Class.attribute`", '``Class.attribute``'),
        (":py:attr:`Class.attribute`", '``Class.attribute``'),
    ],
)
def test_replace_attrs_on_xrefs(input_str, expected_output):
    """Test replace_attrs() function with proper input"""
    assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize(
    "input_str",
    [
        # Short Refs
        "``:attr:`~attribute```",
        "``:attr:`~.attribute```",
        "``:attr:`~.Class.attribute```",
        "``:attr:`~Class.attribute```",
        "``:py:attr:`~attribute```",
        "``:py:attr:`~.attribute```",
        "``:py:attr:`~.Class.attribute```",
        "``:py:attr:`~Class.attribute```",
        # Long Refs
        "``:attr:`attribute```",
        "``:attr:`.attribute```",
        "``:attr:`.Class.attribute```",
        "``:attr:`Class.attribute```",
        "``:py:attr:`attribute```",
        "``:py:attr:`.attribute```",
        "``:py:attr:`.Class.attribute```",
        "``:py:attr:`Class.attribute```",
    ],
)
def test_replace_attrs_with_inline_literals(input_str):
    """If a cross-reference is within an inline literal, it shouldn't be replaced."""
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        # Short refs
        ("The :attr:`~attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :attr:`~.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :attr:`~.Class.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :attr:`~Class.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`~attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`~.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`~.Class.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`~Class.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        # Long Refs
        ("The :attr:`attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :attr:`.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :attr:`.Class.attribute` cross-ref", 'The ``Class.attribute`` cross-ref'),
        ("The :attr:`Class.attribute` cross-ref", 'The ``Class.attribute`` cross-ref'),
        ("The :py:attr:`attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`.attribute` cross-ref", 'The ``attribute`` cross-ref'),
        ("The :py:attr:`.Class.attribute` cross-ref", 'The ``Class.attribute`` cross-ref'),
        ("The :py:attr:`Class.attribute` cross-ref", 'The ``Class.attribute`` cross-ref'),
    ],
)
def test_replace_attrs_within_sentence(input_str, expected_output):
    assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize(
    "input_str",
    [
        # Short refs
        "The:attr:`~attribute` cross-ref",
        "The:attr:`~.attribute` cross-ref",
        "The:attr:`~.Class.attribute` cross-ref",
        "The:attr:`~Class.attribute` cross-ref",
        "The:py:attr:`~attribute` cross-ref",
        "The:py:attr:`~.attribute` cross-ref",
        "The:py:attr:`~.Class.attribute` cross-ref",
        "The:py:attr:`~Class.attribute` cross-ref",
        # Long Refs
        "The:attr:`attribute` cross-ref",
        "The:attr:`.attribute` cross-ref",
        "The:attr:`.Class.attribute` cross-ref",
        "The:attr:`Class.attribute` cross-ref",
        "The:py:attr:`attribute` cross-ref",
        "The:py:attr:`.attribute` cross-ref",
        "The:py:attr:`.Class.attribute` cross-ref",
        "The:py:attr:`Class.attribute` cross-ref",
    ],
)
def test_replace_attrs_no_preceding_whitespace(input_str):
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize(
    "input_str",
    [
        # Short refs
        "The :attr:`~attribute`cross-ref",
        "The :attr:`~.attribute`cross-ref",
        "The :attr:`~.Class.attribute`cross-ref",
        "The :attr:`~Class.attribute`cross-ref",
        "The :py:attr:`~attribute`cross-ref",
        "The :py:attr:`~.attribute`cross-ref",
        "The :py:attr:`~.Class.attribute`cross-ref",
        "The :py:attr:`~Class.attribute`cross-ref",
        # Long Refs
        "The :attr:`attribute`cross-ref",
        "The :attr:`.attribute`cross-ref",
        "The :attr:`.Class.attribute`cross-ref",
        "The :attr:`Class.attribute`cross-ref",
        "The :py:attr:`attribute`cross-ref",
        "The :py:attr:`.attribute`cross-ref",
        "The :py:attr:`.Class.attribute`cross-ref",
        "The :py:attr:`Class.attribute`cross-ref",
    ],
)
def test_replace_attrs_no_trailing_whitespace(input_str):
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize(
    "input_str,expected_output",
    [
        # Short refs
        ("The :attr:`~attribute`:", 'The ``attribute``:'),
        ("The :attr:`~.attribute`:", 'The ``attribute``:'),
        ("The :attr:`~.Class.attribute`:", 'The ``attribute``:'),
        ("The :attr:`~Class.attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`~attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`~.attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`~.Class.attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`~Class.attribute`:", 'The ``attribute``:'),
        # Long Refs
        ("The :attr:`attribute`:", 'The ``attribute``:'),
        ("The :attr:`.attribute`:", 'The ``attribute``:'),
        ("The :attr:`.Class.attribute`:", 'The ``Class.attribute``:'),
        ("The :attr:`Class.attribute`:", 'The ``Class.attribute``:'),
        ("The :py:attr:`attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`.attribute`:", 'The ``attribute``:'),
        ("The :py:attr:`.Class.attribute`:", 'The ``Class.attribute``:'),
        ("The :py:attr:`Class.attribute`:", 'The ``Class.attribute``:'),
    ],
)
def test_replace_attrs_with_trailing_colon(input_str, expected_output):
    """A colon after a cross-reference should not stop it from being replaced"""
    assert replace_attrs(input_str) == expected_output
