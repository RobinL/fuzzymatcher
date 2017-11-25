# -*- coding: utf-8 -*-

import abc

class ScorerABC:

    """
    A DataPreprocessor is responsible for ingesting df_left (the dataframe containing the records we
    want to find matches for) and df_right (the dataframe we want to search for potential matches)
    and applying preprocessing stages like normalisation to make matching easier.
    """

    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def add_data(self, matcher):
        pass


    @abc.abstractmethod
    def get_freq(token):
        pass

    @abc.abstractmethod
    def score_match(record_to_find_match, record_potential_match):
        pass

