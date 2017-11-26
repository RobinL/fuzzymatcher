# -*- coding: utf-8 -*-

from fuzzymatcher.data_preprocessor_abc import DataPreprocessorABC
from metaphone import doublemetaphone

class DataPreprocessor(DataPreprocessorABC):

    def __init__(self, dmetaphone = True):
        self.include_dmetaphone = dmetaphone

    def add_data(self, matcher):

        """Adds data and parameters the DataPreprocessor needs to run

        This is similar to an __init__ method, except it is run after the object is instantiated.

        Returns:
            None
        """

        self.matcher = matcher

    def preprocess(self):

        left_cols = self.matcher.left_on
        right_cols = self.matcher.right_on

        # Name collisions mean that we want to rename the id columns
        if not self.matcher.left_id_col:
            self.add_id(self.matcher.df_left, "left")
            self.matcher.left_id_col = "__id_left"
        else:
            self.matcher.df_left.rename(columns = {self.matcher.left_id_col: "__id_left"})

        if not self.matcher.right_id_col:
            self.add_id(self.matcher.df_right, "right")
            self.matcher.right_id_col = "__id_right"
        else:
            self.matcher.df_right.rename(columns = {self.matcher.right_id_col: "__id_right"})

        self._concat_all_fields(self.matcher.df_left, left_cols)
        self._concat_all_fields(self.matcher.df_right, right_cols)

        self._case_and_punctuation(self.matcher.df_left)
        self._case_and_punctuation(self.matcher.df_right)

        # Add dmetaphone to everything that looks like a word
        if self.include_dmetaphone:
            self._add_dmetaphone(self.matcher.df_left)
            self._add_dmetaphone(self.matcher.df_right)

        self.matcher.df_left_processed = self.matcher.df_left[[self.matcher.left_id_col, "_concat_all"]]
        self.matcher.df_right_processed = self.matcher.df_right[[self.matcher.right_id_col, "_concat_all"]]

    @staticmethod
    def _concat_all_fields(df, cols):
        # Note no return needed because dfs are mutable and pass by ref
        df['_concat_all'] = df[cols].apply(' '.join, axis=1)

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

    @staticmethod
    def _add_dmetaphone(df):

        def add_dmetaphone_to_string(x):
            tokens = x.split(" ")
            new_tokens = []
            for t in tokens:
                dmp = doublemetaphone(t)
                if dmp[0] == '':
                    pass
                elif dmp[1] == '':
                    new_tokens.append(dmp[0])
                else:
                    new_tokens.extend(dmp)
            tokens.extend(new_tokens)
            return " ".join(tokens)

        df["_concat_all"] =  df["_concat_all"].apply(add_dmetaphone_to_string)
