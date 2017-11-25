# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter
from itertools import chain

class Scorer:

    """
    A DataPreprocessor is responsible for ingesting df_left (the dataframe containing the records we
    want to find matches for) and df_right (the dataframe we want to search for potential matches)
    and applying preprocessing stages like normalisation to make matching easier.
    """

    def add_data(self, matcher):
        self.matcher = matcher
        self.prob_dict = {}

        self.generate_probs()


    def get_prob(self, token):
        return self.probs_dict[token]


    def score_match(self, record_to_find_match, record_potential_match):
        record_potential_match.match_score = 10



    def generate_probs(self):

        series1 = self.matcher.df_left_processed["_concat_all"]
        series2 = self.matcher.df_right_processed["_concat_all"]
        all_series = pd.concat([series1, series2])

        tokens = list(chain.from_iterable(all_series.apply(str.split)))
        freq_counts = Counter(tokens)
        total_token_count = sum(freq_counts.values())
        probs_dict = {k: freq_counts[k]*1.0/total_token_count for k in freq_counts}

        self.probs_dict = probs_dict

