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
        test1 = addme(1, 2) == 4
        print("testing first thing")
        self.assertTrue(test1, "Adding two numbers should give the correct answer")

if __name__ == '__main__':
    unittest.main()
