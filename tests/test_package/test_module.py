class TestClass:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def test_method(self):
        pass


def test_function(*args, **kwargs):
    return args, kwargs


