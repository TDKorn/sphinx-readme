import pytest
from sphinx.testing.path import path
from tests.helpers import assert_doctree_equal


@pytest.mark.sphinx(
    buildername='html',
    freshenv=True,
)
@pytest.mark.parametrize("confoverrides, expected_filename", [
    ({}, "rubric_markup_raw"),
    ({"readme_rubric_heading": "z"}, "rubric_markup_raw"),  # Invalid heading -> use markup
    ({"readme_rubric_heading": "="}, "rubric_heading_raw"),
    ({"readme_raw_directive": False}, "rubric_markup_list_table"),
    ({"readme_rubric_heading": "=", "readme_raw_directive": False}, "rubric_heading_list_table"),
])
def test_rubrics(confoverrides, expected_filename, src_dir, app_params, make_app, get_generated_doctree, get_expected_doctree):
    src_file = "rubric.rst"
    filenames = [src_dir.joinpath(src_file)]
    confoverrides["readme_src_files"] = src_file

    args, kwargs = app_params
    kwargs.update({
        "confoverrides": confoverrides,
        "srcdir": path(src_dir)
    })
    app = make_app(*args, **kwargs)
    app.build(filenames=filenames)

    expected = get_expected_doctree(app, "rubric", expected_filename)
    generated = get_generated_doctree(app, src_file)
    assert_doctree_equal(generated, expected)

