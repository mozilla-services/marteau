from unittest import TestCase
import json

from cornice.tests import CatchErrors
from pyramid import testing
from redis import Redis
from webtest import TestApp
from marteau.web import main as wsgi_endpoint


class TestSharedMemory(TestCase):

    def __init__(self, *args, **kwargs):

        # we don't want the redis connection to be recreated each time we
        # pass to the next test, so we instanciate it here.
        self.redis = Redis()
        self.valid_data = json.dumps({'key': 'value'})
        super(TestSharedMemory, self).__init__(*args, **kwargs)

    def setUp(self):

        self.config = testing.setUp()
        self.app = TestApp(CatchErrors(wsgi_endpoint()))

    def tearDown(self):
        testing.tearDown()

    def test_404(self):
        # error out if the resource doesn't exist
        self.app.get('/data/foobar', status=404)

    def test_valid_resource_creation(self):

        try:
            # a PUT on an unknown resource should work and return 201
            self.app.put('/data/foobar', self.valid_data, status=201,
                         headers={'Accept': 'application/json'})

            # let's check that the data is stored in the redis server,
            # under the right name
            self.assertEquals(self.redis.get('foobar'), self.valid_data)
        finally:
            # and finally delete it!
            self.redis.delete('foobar')

    def test_double_resource_creation(self):
        try:
            # If we PUT two times, we should get a conflict the second time.
            self.app.put('/data/foobar', self.valid_data, status=201)
            self.app.put('/data/foobar', self.valid_data, status=409)
        finally:
            # and finally delete it!
            self.redis.delete('foobar')

    def test_resource_creation_without_data(self):
        self.app.put('/data/foobar', status=400)
        self.assertIsNone(self.redis.get('foobar'))

    def test_resource_creation_with_invalid_json(self):
        try:
            invalid_json = '{this is invalid'
            # we don't care about the format of the data sent on the server
            self.app.put('/data/foobar', invalid_json, status=201)
        finally:
            self.redis.delete('foobar')

    def test_resource_deletion(self):
        try:
            self.redis.set('foobar', 'data')
            self.app.delete('/data/foobar')
        finally:
            self.redis.delete('foobar')
