from funkload.FunkLoadTestCase import FunkLoadTestCase


class StupidTest(FunkLoadTestCase):

    def test_simple(self):
        res = self.get('http://google.com')
        self.assertEquals(res.code, 200)


if __name__ == '__main__':
    import unittest
    unittest.main()
