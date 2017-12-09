# -*- coding: utf-8 -*-

from functools import lru_cache

from fuzzymatcher.data_preprocessor_abc import DataPreprocessorABC
from metaphone import doublemetaphone

class DataPreprocessor(DataPreprocessorABC):

    """
    Normalise and deal with IDs
    """

    def __init__(self, dmetaphone = True):
        self.include_dmetaphone = dmetaphone

    def register_matcher(self, matcher):
        self.matcher = matcher

    def preprocess(self):

        left_cols = self.matcher.left_on
        right_cols = self.matcher.right_on

        # Name collisions mean that we want to rename the id columns
        if not self.matcher.left_id_col:
            self.add_id(self.matcher.df_left, "left")
            self.matcher.left_id_col = "__id_left"
        else:
            self.matcher.df_left.rename(columns={self.matcher.left_id_col: "__id_left"}, inplace=True)

        if not self.matcher.right_id_col:
            self.add_id(self.matcher.df_right, "right")
            self.matcher.right_id_col = "__id_right"
        else:
            self.matcher.df_right.rename(columns={self.matcher.right_id_col: "__id_right"}, inplace=True)



    @staticmethod
    def _concat_all_fields(df, cols):
        # Note no return needed because dfs are mutable and pass by ref
        df[cols] = df[cols].fillna("NULL")
        df['_concat_all'] = df[cols].apply(' '.join, axis=1)

    @staticmethod
    def _alternative_tokens_all_fields(df):
        df["_concat_all_alternatives"] = df["_concat_all"].apply(DataPreprocessor._concat_all_to_alternatives)

    @staticmethod
    def _concat_all_to_alternatives(concat_all):
        tokens = concat_all.split(" ")
        misspellings = []
        for t in tokens:
            token_misspellings = DataPreprocessor._get_misspellings(t)
            misspellings.extend(token_misspellings)
        return " ".join(misspellings)

    @staticmethod
    @lru_cache(maxsize=int(1e5))
    def _get_misspellings(token):
        """
        Must return a list of misspellings
        If there are no misspellings, just return a list of length 0
        """
        misspellings = doublemetaphone(token)
        misspellings = [t for t in misspellings if t != ""]
        return misspellings

    @staticmethod
    @lru_cache(maxsize=int(1e5))
    def _is_mispelling(token1, token2):
        mis_t1 = set(DataPreprocessor._get_misspellings(token1))
        mis_t2 = set(DataPreprocessor._get_misspellings(token2))
        common = mis_t1.intersection(mis_t2).difference({''})  # Difference in case '' included in tokens
        return len(common) > 0

    @staticmethod
    def _case_and_punctuation(df):
        df['_concat_all'] = df['_concat_all'].str.upper()
        df['_concat_all'] = df['_concat_all'].str.replace("'","")
        df['_concat_all'] = df['_concat_all'].str.replace('[^\w\s]',' ')
        df['_concat_all'] = df['_concat_all'].str.replace('\s{2,100}',' ')

    @staticmethod
    def add_id(df, prefix):
        id_colname = "__id_" + prefix
        data = range(0, len(df))
        data = ["{}_{}".format(i, prefix) for i in data]
        df.insert(0, id_colname, data)
