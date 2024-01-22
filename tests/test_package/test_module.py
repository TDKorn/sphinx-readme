from functools import cached_property


TEST_VARIABLE = 'test_value'  #: This is a variable docstring


class TestClass:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.test_attr = 0  #: This is an attribute docstring

    def test_method(self):
        return self.kwargs

    @property
    def test_property(self):
        return self.args

    @cached_property
    def test_cached_property(self):
        return self.test_attr * 0


class TestException(Exception):
    def __init__(self, *args):
        super().__init__(*args)


def test_function(*args, **kwargs):
    return args, kwargs

