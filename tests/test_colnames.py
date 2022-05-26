# -*- coding: utf-8 -*-

"""
Tests
"""

import unittest
from fuzzymatcher import link_table
import pandas as pd

'''
The data path does not seem to be correct, judging from what
was created using 'create_fake_dataset.ipynb'. Correcting it to match
true locations (data folder within tests folder).
'''
# "tests/data/left_2.csv" (original left data path)
# "tests/data/right_2.csv" (original right data path)
left_1_path = "./data/left_1.csv"
right_1_path = "./data/right_1.csv"
left_2_path = "./data/left_2.csv"
right_2_path = "./data/right_2.csv"

class ColNameCollisions(unittest.TestCase):
    """
    Test what happens when the user provides input data with
    some column names which are the same in each dataset
    """



    
    def test_all_colnames_match(self):
        """
        Adding two numbers should give the correct answer
        """
        left = pd.read_csv(left_2_path)
        right = pd.read_csv(right_2_path)
        left_on = ["fname", "mname", "lname",  "dob"]
        right_on = ["fname", "mname", "lname",  "dob"]

        df = link_table(left, right, left_on, right_on)

        expected_columns = ['__id_left',
                      '__id_right',
                      'match_score',
                      'match_rank',
                      'fname_left',
                      'fname_right',
                      'mname_left',
                      'mname_right',
                      'lname_left',
                      'lname_right',
                      'dob_left',
                      'dob_right']

        actual_columns = list(df.columns)
        self.assertEqual(expected_columns, actual_columns)

    def test_all_colnames_match_with_id(self):
        """
        Adding two numbers should give the correct answer
        """
        left = pd.read_csv(left_2_path)
        right = pd.read_csv(right_2_path)
        left_on = ["fname", "mname", "lname",  "dob"]
        right_on = ["fname", "mname", "lname",  "dob"]

        df = link_table(left, right, left_on, right_on, left_id_col="id", right_id_col="id")

        expected_columns = ['__id_left',
                    '__id_right',
                    'match_score',
                    'match_rank',
                    'fname_left',
                    'fname_right',
                    'mname_left',
                    'mname_right',
                    'lname_left',
                    'lname_right',
                    'dob_left',
                    'dob_right']

        actual_columns = list(df.columns)
        self.assertEqual(expected_columns, actual_columns)

    def test_some_colnames_match(self):
        """
        Adding two numbers should give the correct answer
        """
        left = pd.read_csv(left_1_path)
        left = left.rename(columns = {"fname": "name"})
        right = pd.read_csv(right_1_path)
        left_on = ["name", "mname", "lname",  "dob"]
        right_on = ["name", "middlename", "surname", "date"]

        df = link_table(left, right, left_on, right_on)

        expected_columns = ['__id_left',
                            '__id_right',
                            'match_score',
                            'match_rank',
                            'name_left',
                            'name_right',
                            'mname',
                            'middlename',
                            'lname',
                            'surname',
                            'dob',
                            'date']

        actual_columns = list(df.columns)
        self.assertEqual(expected_columns, actual_columns)


if __name__ == '__main__':
    unittest.main()
