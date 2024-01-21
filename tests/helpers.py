from pathlib import Path
from itertools import zip_longest
from sphinx.testing import restructuredtext
from sphinx.testing.util import SphinxTestApp
from docutils.nodes import Text, Element, system_message, document


def parse_doctree(filepath: Path, app: SphinxTestApp) -> document:
    """Parses an RST file into a doctree"""
    if not filepath.exists():
        raise FileNotFoundError(
            f"File doesn't exist: {filepath}"
        )
    rst = filepath.read_text(encoding='utf-8')
    return restructuredtext.parse(app, rst, filepath.stem)


def assert_doctree_equal(generated_doctree, expected_doctree):
    """Compares two doctrees, ignoring any whitespace changes"""
    generated_nodes = generated_doctree.traverse(include_self=False)
    expected_nodes = expected_doctree.traverse(include_self=False)

    for generated, expected in zip_longest(generated_nodes, expected_nodes):
        assert_node_equal(generated, expected)


def assert_node_equal(generated, expected):
    """Compares two nodes"""
    assert type(generated) == type(expected)

    if isinstance(generated, Text):
        assert generated.astext() == expected.astext()

    elif isinstance(generated, system_message):
        assert len(generated.children) == len(expected.children)

    elif isinstance(generated, Element):
        assert len(generated.children) == len(expected.children)
        assert generated.attributes == expected.attributes

    else:
        raise AssertionError

