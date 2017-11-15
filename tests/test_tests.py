# -*- coding: utf-8 -*-

"""
Tests
"""

import unittest
from addme.mymodule import addme

class AddTest(unittest.TestCase):
    """
    Test the add function
    """

    def test_add_fn(self):
        """
        Adding two numbers should give the correct answer
        """
        test1 = addme(1, 2) == 3
        print("testing first thing")
        self.assertTrue(test1, "Adding two numbers should give the correct answer")

if __name__ == '__main__':
    unittest.main()
