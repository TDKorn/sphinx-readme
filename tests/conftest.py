import pytest
import shutil
from pathlib import Path
from sphinx.testing import restructuredtext


pytest_plugins = 'sphinx.testing.fixtures'


@pytest.fixture(scope='session')
def src_dir():
    return (Path(__file__).parent / 'datasets').resolve()


@pytest.fixture(scope='session')
def expected_dir():
    return (Path(__file__).parent / 'expected').resolve()


@pytest.fixture
def output_dir():
    out_dir = (Path(__file__).parent / 'output').resolve()
    out_dir.mkdir(exist_ok=True)

    yield out_dir

    shutil.rmtree(out_dir, ignore_errors=True)


@pytest.fixture(scope="session", autouse=True)
def remove_sphinx_builds(src_dir):
    """Remove all build directories from the test folder"""
    yield

    build_dir = (src_dir/"_build")
    shutil.rmtree(build_dir, ignore_errors=True)


@pytest.fixture
def get_expected_doctree(expected_dir):
    def _get_expected(app, subdir, file):
        filepath = (expected_dir/subdir/f"{file}.rst")
        if not filepath.exists():
            raise FileNotFoundError(
                f"Expected file doesn't exist: {filepath}"
            )
        rst = filepath.read_text(encoding='utf-8')
        return restructuredtext.parse(app, rst, file)

    return _get_expected


@pytest.fixture
def get_generated_doctree(output_dir):
    def _get_generated(app, file):
        filepath = (output_dir/file)
        if not filepath.exists():
            raise FileNotFoundError(
                f"Output file doesn't exist: {filepath}"
            )
        rst = filepath.read_text(encoding='utf-8')
        return restructuredtext.parse(app, rst, file)

    return _get_generated

