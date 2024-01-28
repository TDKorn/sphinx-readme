import pytest
from tests.helpers import assert_doctree_equal


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_file", [
    # Test cases with raw directive
    ({}, "rubric_markup_raw.rst"),
    ({"readme_rubric_heading": "="}, "rubric_heading_raw.rst"),
    # Test cases without raw directive
    ({"readme_raw_directive": False}, "rubric_markup_list_table.rst"),
    ({"readme_rubric_heading": "=", "readme_raw_directive": False}, "rubric_heading_list_table.rst"),
    # Test cases with invalid heading -> should use markup
    ({"readme_rubric_heading": "z"}, "rubric_markup_raw.rst"),
    ({"readme_rubric_heading": "z", "readme_raw_directive": False}, "rubric_markup_list_table.rst"),
])
def test_rubrics(confoverrides, expected_file, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "directives/rubric.rst"
    src_files = {src_file: expected_file}
    app = build_sphinx(
        src_files=src_files,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, src_file, expected_file)
    generated = get_generated_doctree(app, expected_file)
    assert_doctree_equal(generated, expected)


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_file", [
    ({}, "substitution_xrefs_with_intersphinx.rst"),
    ({'intersphinx_mapping': {}}, "substitution_xrefs_without_intersphinx.rst")
])
def test_substitution_xrefs(confoverrides, expected_file, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "cross_references/substitution_xrefs.rst"
    src_files = {src_file: expected_file}
    app = build_sphinx(
        src_files=src_files,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, src_file, expected_file)
    generated = get_generated_doctree(app, expected_file)
    assert_doctree_equal(generated, expected)


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_file", [
    ({'readme_docs_url_type': 'html'}, "html_links.rst"),
    ({'readme_docs_url_type': 'code'}, "code_links.rst"),
    ({'readme_docs_url_type': 'html', 'readme_inline_markup': False}, "html_links_no_inline_markup.rst"),
    ({'readme_docs_url_type': 'code', 'readme_inline_markup': False}, "code_links_no_inline_markup.rst")
])
def test_python_xrefs(confoverrides, expected_file, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "cross_references/python_xrefs.rst"
    src_files = {src_file: expected_file}
    app = build_sphinx(
        src_files=src_files,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, src_file, expected_file)
    generated = get_generated_doctree(app, expected_file)
    assert_doctree_equal(generated, expected)
