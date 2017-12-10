# -*- coding: utf-8 -*-

from functools import lru_cache

from fuzzymatcher.data_preprocessor_abc import DataPreprocessorABC
from metaphone import doublemetaphone

class DataPreprocessor(DataPreprocessorABC):

    """
    Normalise and deal with IDs
    """

    def __init__(self, dmetaphone = True):
        #self.include_dmetaphone = dmetaphone TODO
        pass

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
            self.matcher.df_left["__id_left"] = self.matcher.df_left[self.matcher.left_id_col]

        if not self.matcher.right_id_col:
            self.add_id(self.matcher.df_right, "right")
            self.matcher.right_id_col = "__id_right"
        else:
            self.matcher.df_right["__id_right"] = self.matcher.df_right[self.matcher.right_id_col]


    @staticmethod
    def add_id(df, prefix):
        id_colname = "__id_" + prefix
        data = range(0, len(df))
        data = ["{}_{}".format(i, prefix) for i in data]
        df.insert(0, id_colname, data)
