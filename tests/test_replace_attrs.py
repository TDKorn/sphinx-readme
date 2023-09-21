import pytest
from sphinx_readme.utils.rst import replace_attrs, get_all_xref_variants

test_cases = []
target = "Class.attribute"
variants = get_all_xref_variants(target)

for variant in variants:
    if variant.startswith("~"):
        # Short ref: :attr:`~Class.attr `-> ``attr``
        expected_output = f"``{variant.lstrip('~').split('.')[-1]}``"
    else:
        # Long ref: :attr:`.Class.attr` -> ``Class.attr`
        expected_output = f"``{variant.lstrip('.')}``"

    test_cases.append((f":attr:`{variant}`", expected_output))
    test_cases.append((f":py:attr:`{variant}`", expected_output))

xrefs = list(dict(test_cases))  # The cross-reference from each tuple


@pytest.mark.parametrize("xref,replaced_xref", test_cases)
def test_replace_attrs_on_xrefs(xref, replaced_xref):
    """Test replace_attrs() function with proper input"""
    assert replace_attrs(xref) == replaced_xref


@pytest.mark.parametrize("xref", xrefs)
def test_replace_attrs_with_inline_literals(xref):
    """If a cross-reference is within an inline literal, it shouldn't be replaced."""
    input_str = f"``{xref}``"
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize("xref,replaced", test_cases)
def test_replace_attrs_within_sentence(xref, replaced):
    input_str = f"The {xref} cross-ref"
    expected_output = f"The {replaced} cross-ref"
    assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize("xref", xrefs)
def test_replace_attrs_no_preceding_whitespace(xref):
    input_str = f"The{xref} cross-ref"
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize("xref", xrefs)
def test_replace_attrs_no_trailing_whitespace(xref):
    input_str = f"The {xref}cross-ref"
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize("xref,replaced_xref", test_cases)
def test_replace_attrs_with_trailing_colon(xref, replaced_xref):
    """A colon after a cross-reference should not stop it from being replaced"""
    input_str = f"The {xref}:"
    expected_output = f"The {replaced_xref}:"
    assert replace_attrs(input_str) == expected_output
