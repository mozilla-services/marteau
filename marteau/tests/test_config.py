import os
from unittest import TestCase

from marteau.config import MarteauConfig
from marteau.fixtures import MarteauFixture
from marteau.tests.support import fixture, FakeTestFixture

HERE = os.path.dirname(__file__)


class TestConfig(TestCase):
    def test_config_lookup_modules(self):
        self.assertNotIn(FakeTestFixture, MarteauFixture._abc_registry)
        config = MarteauConfig({'lookup': 'marteau.tests.register_fixtures'})
        config.lookup_modules()
        self.assertIn(FakeTestFixture, MarteauFixture._abc_registry)

    def test_load_fixture(self):
        with fixture(FakeTestFixture) as fix:
            arguments = {'server': 'memcache', 'behavior': 'delay'}
            config = {'fixtures': {'memcache_delay':
                      {'class': 'FakeTestFixture', 'arguments': arguments}}}
            config = MarteauConfig(config)
            memcache_delay = config.get_fixture('memcache_delay')
            memcache_delay.setUp()
            memcache_delay.tearDown()
            self.assertEquals(fix.kwargs, arguments)
            self.assertEquals(fix.config, config)
