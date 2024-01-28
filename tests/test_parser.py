import pytest
from tests.helpers import assert_doctree_equal


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_filename", [
    # Test cases with raw directive
    ({}, "rubric_markup_raw"),
    ({"readme_rubric_heading": "="}, "rubric_heading_raw"),
    # Test cases without raw directive
    ({"readme_raw_directive": False}, "rubric_markup_list_table"),
    ({"readme_rubric_heading": "=", "readme_raw_directive": False}, "rubric_heading_list_table"),
    # Test cases with invalid heading -> should use markup
    ({"readme_rubric_heading": "z"}, "rubric_markup_raw"),
    ({"readme_rubric_heading": "z", "readme_raw_directive": False}, "rubric_markup_list_table"),
])
def test_rubrics(confoverrides, expected_filename, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "rubric.rst"
    subdir = "directives"
    app = build_sphinx(
        subdir=subdir,
        filename=src_file,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, subdir, src_file, expected_filename)
    generated = get_generated_doctree(app, src_file)
    assert_doctree_equal(generated, expected)


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_filename", [
    ({}, "substitution_xrefs_with_intersphinx"),
    ({'intersphinx_mapping': {}}, "substitution_xrefs_without_intersphinx")
])
def test_substitution_xrefs(confoverrides, expected_filename, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "substitution_xrefs.rst"
    subdir = "cross_references"
    app = build_sphinx(
        subdir=subdir,
        filename=src_file,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, subdir, src_file, expected_filename)
    generated = get_generated_doctree(app, src_file)
    assert_doctree_equal(generated, expected)


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_filename", [
    ({'readme_docs_url_type': 'html'}, "html_links"),
    ({'readme_docs_url_type': 'code'}, "code_links"),
    ({'readme_docs_url_type': 'html', 'readme_inline_markup': False}, "html_links_no_inline_markup"),
    ({'readme_docs_url_type': 'code', 'readme_inline_markup': False}, "code_links_no_inline_markup")
])
def test_python_xrefs(confoverrides, expected_filename, app_params, build_sphinx, get_generated_doctree, get_expected_doctree):
    src_file = "python_xrefs.rst"
    subdir = "cross_references"
    app = build_sphinx(
        subdir=subdir,
        filename=src_file,
        app_params=app_params,
        confoverrides=confoverrides
    )
    expected = get_expected_doctree(app, subdir, src_file, expected_filename)
    generated = get_generated_doctree(app, src_file)
    assert_doctree_equal(generated, expected)
