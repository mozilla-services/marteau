import unittest
from marteau.node import Node


class TestNode(unittest.TestCase):

    def test_attr(self):

        node = Node(name='ok', a=1, b=2)
        self.assertEqual(node.a, 1)
