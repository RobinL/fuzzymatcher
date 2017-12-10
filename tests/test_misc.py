import unittest
from fuzzymatcher import link_table
import pandas as pd

class TestNulls(unittest.TestCase):
    """
    Test what happens when the user provides input data with
    null values in some of the cells
    """

    def test_nulls_no_errors(self):
        """
        Adding two numbers should give the correct answer
        """
        df_left = pd.read_csv("tests/data/left_5_nas.csv")
        df_right = pd.read_csv("tests/data/right_5_nas.csv")

        on = ["first_name", "surname", "dob", "city"]

        flj = link_table(df_left, df_right, on, on)