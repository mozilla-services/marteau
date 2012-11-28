import contextlib
from marteau.fixtures import MarteauFixture


class FakeTestFixture(object):

    def __init__(self, config, **kwargs):
        cls = self.cls = FakeTestFixture
        cls.config = config
        cls.kwargs = kwargs
        cls.setup_called = False
        cls.teardown_called = False

    def setUp(self):
        self.cls.setup_called = True

    def tearDown(self):
        self.cls.teardown_called = True

    @classmethod
    def reset(cls):
        cls.kwargs = None
        cls.config = None
        cls.setup_called = None
        cls.teardown_called = None


@contextlib.contextmanager
def fixture(fix=FakeTestFixture):
    MarteauFixture.register(fix)
    yield fix
    MarteauFixture._abc_registry.remove(fix)
    if hasattr(fix, 'reset'):
        fix.reset()
