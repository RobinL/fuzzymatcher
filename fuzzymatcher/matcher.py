# -*- coding: utf-8 -*-
import logging
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta

from fuzzymatcher.record import RecordToMatch, Record
from fuzzymatcher.tokencomparison import TokenComparison
from fuzzymatcher.data_preprocessor_default import DataPreprocessor
from fuzzymatcher.data_getter_sqlite import DataGetter
from fuzzymatcher.scorer_default import Scorer

log = logging.getLogger(__name__)

class Matcher:
    """The Matcher coordinates data matching"""

    def __init__(self,
                 data_preprocessor = DataPreprocessor(),
                 data_getter = DataGetter(),
                 scorer = Scorer(),
                 token_comparison = TokenComparison(),
                 top_n_matches = 5):
        self.token_comparison = token_comparison
        self.data_preprocessor = data_preprocessor
        self.data_getter = data_getter
        self.scorer = scorer
        self.top_n_matches = top_n_matches

    def add_data(self, df_left,
              df_right,
              left_on,
              right_on,
              left_id_col = None,
              right_id_col = None):

        # Copy to prevent modifying the dataframes the user provides
        self.df_left = df_left.copy()
        self.df_right = df_right.copy()

        if type(left_on) == str:
            left_on = [left_on]

        if type(right_on) == str:
            right_on = [right_on]

        self.left_on = left_on
        self.right_on = right_on
        self.left_id_col = left_id_col
        self.right_id_col = right_id_col

        self.left_to_right_lookup = {l:r for (l,r) in zip(left_on, right_on)}

        self.data_preprocessor.register_matcher(self)

    def initiate_records(self):
        self.left_records = {}
        cols = self.left_on.copy()
        cols.append("__id_left")
        df = self.df_left[cols]
        for r in df.iterrows():
            row = r[1]
            fields_dict = dict(row[self.left_on])
            this_id = row["__id_left"]
            rec = RecordToMatch(fields_dict, this_id, self)
            self.left_records[this_id] = rec

        self.right_records = {}
        cols = self.right_on.copy()
        cols.append("__id_right")
        df = self.df_right[cols]
        for r in df.iterrows():
            row = r[1]
            fields_dict = dict(row[self.right_on])
            this_id = row["__id_right"]
            rec = Record(fields_dict, this_id, self)
            self.right_records[this_id] = rec

    def match_all(self):

        # Get a dataset with id, record only for left and right
        self.data_preprocessor.preprocess()

        self.initiate_records()

        # Scorer first because some data getters may need to score records on add_data
        self.scorer.add_data(self)

        self.data_getter.add_data(self)

        # Get a table that contains only the matches, scores and ids
        self.link_table = self._match_processed_data()

    def get_formatted_link_table(self):
        return self._add_original_cols_to_link_table(self.link_table)

    def get_left_join_table(self):
        df = self.df_left.merge(self.link_table, left_on = "__id_left", right_on = "__id_left", how="left")
        df = df.merge(self.df_right, left_on = "__id_right", right_on="__id_right", how="left", suffixes = ("_left", "_right"))

        # Keep records where rank = 1 or there's no rang
        filter1 = df["__rank"] == 1
        filter2 = pd.isnull(df["__rank"])
        df = df[filter1 | filter2]
        df.drop("__rank", axis=1, inplace=True)

        set_cols = ["__score", "__id_left", "__id_right"]

        cols = set_cols.copy()
        cols.extend([c for c in df.columns if c not in set_cols])

        df = df[cols].rename(columns={"__score": "best_match_score"})
        return df

    def _match_processed_data(self):

        # This will store all the records for the link table

        link_table_list = []

        num_left_records = len(self.left_records.keys())
        num_right_records = len(self.right_records.keys())
        log.debug("Matching {} left records against {} right records".format(num_left_records, num_right_records))
        start_time  = datetime.now()

        counter = 0
        total = len(self.left_records.items())
        str_template = "Processed {:,.0f} records, {:.0f}% done in {} minutes and {} seconds"

        for key, this_record in self.left_records.items():

            if (counter) % 1000 == 0 and counter != 0:
                diff = relativedelta(datetime.now(), start_time)
                log.debug(str_template.format(counter, (counter/total)*100, diff.minutes, diff.seconds))

            this_record.find_and_score_potential_matches()
            link_table_list.extend(this_record.get_link_table_rows())

            counter += 1

        diff = relativedelta(datetime.now(), start_time)
        log.debug(str_template.format(counter, (counter/total)*100, diff.minutes, diff.seconds))

        return pd.DataFrame(link_table_list)

    def _add_original_cols_to_link_table(self, link_table):

        df = link_table.merge(self.df_left, left_on = "__id_left", right_on = "__id_left", how = "left", suffixes=('_link', '_left'))

        df = df.merge(self.df_right, left_on = "__id_right", right_on = "__id_right", how="left", suffixes=('_left', "_right"))

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
        rename_dict = {}
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

