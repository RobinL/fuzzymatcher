# -*- coding: utf-8 -*-
from fuzzymatcher.record import RecordToMatch
import pandas as pd

class Matcher:
    """The Matcher coordinates data matching"""

    def __init__(self,
                 data_preprocessor,
                 data_getter,
                 scorer,
                 top_n_matches = 5):
        self.data_preprocessor = data_preprocessor
        self.data_getter = data_getter
        self.scorer = scorer
        self.top_n_matches = top_n_matches

    def add_data(self, df_left,
              df_right,
              left_on,
              right_on,
              left_word_cols = None,
              right_word_cols = None,
              left_id_col = None,
              right_id_col = None):

        # Copy to prevent modifying the dataframes the user provides
        self.df_left = df_left.copy()
        self.df_right = df_right.copy()
        self.left_on = left_on
        self.right_on = right_on
        self.left_word_cols = left_word_cols
        self.right_word_cols = right_word_cols
        self.left_id_col = left_id_col
        self.right_id_col = right_id_col

        self.data_preprocessor.add_data(self)


    def match_all(self):

        # Get a dataset with id, record only for left and right
        self.data_preprocessor.preprocess()

        # Data preprocessor returns list of dicts, not pd.DataFrame
        self.data_getter.add_data(self)
        self.scorer.add_data(self)

        # Get a table that contains only the matches, scores and ids
        link_table = self._match_processed_data()

        link_table = self._add_original_cols_to_link_table(link_table)

        self.link_table = link_table


    def _match_processed_data(self):

        # This will store all the regords for the link table

        link_table_list = []

        for r in self.df_left_processed.iterrows():
            row = r[1]
            record_id = row[self.left_id_col]

            record_to_match = RecordToMatch(record_id, row["_concat_all"], self)

            record_to_match.find_and_score_potential_matches()
            link_table_list.extend(record_to_match.get_link_table_rows())

        return pd.DataFrame(link_table_list)

    def _add_original_cols_to_link_table(self, link_table):

        df = link_table.merge(self.df_left, left_on = "__id_left", right_on = self.left_id_col, how = "left", suffixes=('_link', '_left'))
        df.drop("_concat_all", axis=1, inplace=True)

        df = df.merge(self.df_right, left_on = "__id_right", right_on = self.right_id_col, how="left", suffixes=('_left', "_right"))
        df.drop("_concat_all", axis=1, inplace=True)

        match_cols_left = self.left_on[::-1].copy()
        match_cols_right = self.right_on[::-1].copy()
        col_order = ["__id_left", "__id_right", "__score", "__rank"]
        while len(match_cols_left) > 0 and len(match_cols_right) > 0:

            # Check whether suffixes have been added
            left_col = match_cols_left.pop()
            left_col = self._add_suffix_if_needed(left_col, df, "left")
            col_order.append(left_col)

            right_col = match_cols_right.pop()
            right_col = self._add_suffix_if_needed(right_col, df, "right")
            col_order.append(right_col)

        col_order.extend(match_cols_left)
        col_order.extend(match_cols_right)

        df = df[col_order]

        # Finally rename the id columns back to their original and improve names of score and rank
        if self.left_id_col != self.right_id_col:
            rename_dict = {"__id_left": self.left_id_col,
                           "__id_right": self.right_id_col}
        else:
            rename_dict = {"__id_left": self.left_id_col + "_left",
                           "__id_right": self.right_id_col + "_right"}

        if "match_rank" not in df.columns:
            rename_dict["__rank"] = "match_rank"

        if "match_score" not in df.columns:
            rename_dict["__score"] = "match_score"
        df = df.rename(columns = rename_dict)
        return df

    def _add_suffix_if_needed(self, col_name, df, left_or_right):

        all_cols = df.columns
        if left_or_right == "left":
            left_cols = self.df_left.columns

            if col_name in left_cols and col_name not in all_cols:
                return col_name + "_left"
            else:
                return col_name

        if left_or_right == "right":
            right_cols = self.df_right.columns
            if col_name in right_cols and col_name not in all_cols:
                return col_name + "_right"
            else:
                return col_name










