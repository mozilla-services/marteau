from abc import ABCMeta, abstractmethod


class MarteauFixture(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_name(self):
        return NotImplemented

    @abstractmethod
    def get_arguments(self):
        return NotImplemented

    @abstractmethod
    def set_up(self):
        return NotImplemented

    @abstractmethod
    def tear_down(self):
        return NotImplemented

    @classmethod
    def register(cls, subclass):
        ABCMeta.register(cls, subclass)
        if subclass not in cls._abc_registry:
            cls._abc_registry.add(subclass)

    @classmethod
    def get_fixtures(cls):
        return dict([(klass.get_name(), klass)
                     for klass in cls._abc_registry])

    @classmethod
    def get_fixture(cls, name):
        return cls.get_fixtures().get(name)


get_fixtures = MarteauFixture.get_fixtures
get_fixture = MarteauFixture.get_fixture
