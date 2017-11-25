# -*- coding: utf-8 -*-

class Matcher:
    """The Matcher coordinates data matching"""

    def __init__(self,
                 data_preprocessor,
                 data_getter,
                 scorer,
                 df_left = None,
                 df_right = None,
                 top_n_matches = 5):

        self.df_left = df_left
        self.df_right = df_right

        # QUESTION:  could se just do self.data_preprocessor = left
        self.data_preprocessor.df_left = df_left
        self.data_preprocessor.df_right = df_right

        self.scorer = scorer

    def match_all(self):

        # Get a dataset with id, record only for left and right
        self.data_preprocessor.preprocess()

        # Data preprocessor returns list of dicts, not pd.DataFrame
        self.data_getter.add_data(self.data_preprocessor.data_search_within)

        self.scorer.add_data(self.data_preprocessor.data_search_within, self.data_preprocessor.data_find_match_for)

        # Get a table with
        _match_processed_data

        # Create a final link_table with fields from original data
        _format_results()



    # ALWAYS INCLUDE UP TO x matches
    def _match_processed_data(self):

        # Probably work entirely in dictionaries here.  No pandas


    def find
        data_getter.get_potential_matches_from_record()
