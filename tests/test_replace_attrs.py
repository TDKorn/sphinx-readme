import pytest
from sphinx_readme.utils.rst import replace_attrs, get_all_xref_variants, AFTER_XREF, BEFORE_XREF

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
    """Cross-references should not be replaced if they are preceded by any non-whitespace character
    other than the :attr:`~.utils.rst.BEFORE_XREF` characters.
    """
    input_str = f"The{xref} cross-ref"
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize("xref,replaced", test_cases)
def test_replace_attrs_only_preceding_whitespace(xref, replaced):
    input_str = f"   {xref} cross-ref"
    expected_output = f"   {replaced} cross-ref"
    assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize("xref", xrefs)
def test_replace_attrs_no_trailing_whitespace(xref):
    """Cross-references should not be replaced if they are followed by any non-whitespace character
    other than the :attr:`~.utils.rst.AFTER_XREF` characters.
    """
    input_str = f"The {xref}cross-ref"
    assert replace_attrs(input_str) == input_str


@pytest.mark.parametrize("xref,replaced", test_cases)
def test_replace_attrs_only_trailing_whitespace(xref, replaced):
    input_str = f"The {xref}   "
    expected_output = f"The {replaced}   "
    assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize("xref,replaced", test_cases)
def test_replace_attrs_trailing_newline(xref, replaced):
    input_str = f"The {xref}\n"
    expected_output = f"The {replaced}\n"
    assert replace_attrs(input_str) == expected_output


# Redefine these constants since the ones in ``rst.py`` are escaped
BEFORE_XREF = ":[{(/\"'-"
AFTER_XREF = ":;!?,\"'/\\])}-"


@pytest.mark.parametrize("xref,replaced_xref", test_cases)
def test_replace_attrs_with_preceding_acceptable_chars(xref, replaced_xref):
    """Cross-references should be replaced if they're preceded by any of the :attr:`~.rst.BEFORE_XREF` characters"""
    for char in BEFORE_XREF:
        input_str = rf"The {char}{xref}"
        expected_output = f"The {char}{replaced_xref}"
        assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize("xref,replaced_xref", test_cases)
def test_replace_attrs_with_trailing_acceptable_chars(xref, replaced_xref):
    """Cross-references should be replaced if they're followed by any of the :attr:`~.rst.AFTER_XREF` characters"""
    for char in AFTER_XREF:
        input_str = rf"The {xref}{char}"
        expected_output = f"The {replaced_xref}{char}"
        assert replace_attrs(input_str) == expected_output


@pytest.mark.parametrize("xref,replaced_xref", test_cases)
def test_replace_attrs_surrounded_by_acceptable_chars(xref, replaced_xref):
    """Cross-references preceded by any of the :attr:`~.rst.BEFORE_XREF` characters and followed by any
    of the :attr:`~.rst.AFTER_XREF` characters should be replaced.

    This test may be overkill.
    """
    for prefix in BEFORE_XREF:
        for suffix in AFTER_XREF:
            input_str = rf"The {prefix}{xref}{suffix}"
            expected_output = f"The {prefix}{replaced_xref}{suffix}"
            assert replace_attrs(input_str) == expected_output
