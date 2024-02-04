import pytest
import shutil
from pathlib import Path
from typing import List, Dict
from sphinx.testing.path import path
from tests.helpers import parse_doctree


pytest_plugins = 'sphinx.testing.fixtures'


@pytest.fixture(scope='session')
def src_dir():
    return (Path(__file__).parent / 'datasets').resolve()


@pytest.fixture(scope='session')
def expected_dir():
    return (Path(__file__).parent / 'expected').resolve()


@pytest.fixture(scope='session')
def output_dir():
    """Directory where generated files are written"""
    output_dir = (Path(__file__).parent / 'output').resolve()
    output_dir.mkdir(exist_ok=True)
    return output_dir


@pytest.fixture(scope="session", autouse=True)
def remove_output_from_sphinx_builds(src_dir, output_dir):
    """Removes the build and output directories from the test folder"""
    yield

    shutil.rmtree(src_dir.joinpath('_build'), ignore_errors=True)
    shutil.rmtree(output_dir, ignore_errors=True)


@pytest.fixture()
def build_sphinx(src_dir, output_dir, make_app):
    """Provides a function to run a Sphinx build with a specific file"""

    def _build(app_params, src_files: str | List[str] | Dict[str, str], confoverrides: dict, force_all=False):
        confoverrides["readme_src_files"] = src_files
        filenames = [src_dir.joinpath(src_file) for src_file in src_files]

        args, kwargs = app_params
        kwargs.update({
            "confoverrides": confoverrides,
            "srcdir": path(src_dir)
        })
        app = make_app(*args, **kwargs)
        app.build(filenames=filenames, force_all=force_all)
        return app

    yield _build

    # Clear contents of output directory after each test
    shutil.rmtree(output_dir, ignore_errors=True)
    output_dir.mkdir(exist_ok=True)


@pytest.fixture(scope='session')
def get_expected_doctree(expected_dir):
    """Provides a function to parse an expected output file into a doctree"""
    def _get_expected(app, src_file, expected_file):
        subdir = src_file.removesuffix('.rst')
        filepath = (expected_dir/subdir/expected_file)
        return parse_doctree(filepath, app)

    return _get_expected


@pytest.fixture(scope='session')
def get_generated_doctree(output_dir):
    """Provides a function to parse a file generated by a Sphinx build into a doctree"""
    def _get_generated(app, out_file):
        filepath = (output_dir/out_file)
        return parse_doctree(filepath, app)

    return _get_generated

