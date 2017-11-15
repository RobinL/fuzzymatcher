# -*- coding: utf-8 -*-

"""
Tests
"""

import unittest
from fuzzymatcher.delete import addme

class AddTest(unittest.TestCase):
    """
    Test the add function
    """

    def test_add_fn(self):
        """
        Adding two numbers should give the correct answer
        """
        t1 = addme(1, 2) == 3
        self.assertTrue(t1)

if __name__ == '__main__':
    unittest.main()
