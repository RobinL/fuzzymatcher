# -*- coding: utf-8 -*-

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

        self.scorer = scorer

    def add_data(self, df_left,
              df_right,
              left_on,
              right_on,
              left_word_cols = None,
              right_word_cols = None,
              left_id_col = None,
              right_id_col = None,):

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
        #return self.data_getter.get_potential_matches_from_record("hello")
        # self.scorer.add_data(self.data_preprocessor.data_search_within, self.data_preprocessor.data_find_match_for)



        # Get a table with
        # _match_processed_data

        # Create a final link_table with fields from original data
        # _format_results()



    # ALWAYS INCLUDE UP TO x matches
    def _match_processed_data(self):

        # Probably work entirely in dictionaries here.  No panda
        pass


