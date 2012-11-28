from unittest2 import TestCase

from marteau.fixtures import get_fixtures
from marteau.tests.support import fixture, FakeTestFixture


class TestFixtures(TestCase):

    def test_plugin_registration(self):
        with fixture(FakeTestFixture):
            self.assertEquals({'FakeTestFixture': FakeTestFixture},
                              get_fixtures())
