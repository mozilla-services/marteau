from abc import ABCMeta, abstractmethod


class MarteauFixture(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self, **kwargs):
        return NotImplemented

    @abstractmethod
    def setUp(self):
        return NotImplemented

    @abstractmethod
    def tearDown(self):
        return NotImplemented

    @classmethod
    def register(cls, subclass):
        ABCMeta.register(cls, subclass)
        if subclass not in cls._abc_registry:
            cls._abc_registry.add(subclass)

    @classmethod
    def get_fixtures(cls):
        return dict([(getattr(klass, 'name', klass.__name__), klass)
                     for klass in cls._abc_registry])

    @classmethod
    def get_fixture(cls, name):
        return cls.get_fixtures().get(name)


get_fixtures = MarteauFixture.get_fixtures
get_fixture = MarteauFixture.get_fixture
