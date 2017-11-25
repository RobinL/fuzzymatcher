# -*- coding: utf-8 -*-

import abc

class DataPreprocessorABC:

    """
    A DataPreprocessor is responsible for ingesting df_left (the dataframe containing the records we
    want to find matches for) and df_right (the dataframe we want to search for potential matches)
    and applying preprocessing stages like normalisation to make matching easier.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_data(self,
                 df_left,
                 df_right,
                 left_on,
                 right_on,
                 left_word_cols=None,
                 right_word_cols=None,
                 left_id_col=None,
                 right_id_col=None):

        """Adds data and parameters the DataPreprocessor needs to run

        This is similar to an __init__ method, except it is run after the object is instantiated.

        Returns:
            None
        """



    @abc.abstractmethod
    def preprocess(self):
        """Main method that runs the data preprocesing

        Creates two new attributes on the data preprocessor object:

        data_search_within:
        This is a list of dictionaries like this:  {"id": record_id, "data:" normalised string}

        data_find_match_for:
        This is a list of dictionaries like this:  {"id": record_id, "data:" normalised string}

        Returns:
            None
        """
