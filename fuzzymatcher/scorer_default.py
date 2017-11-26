# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter
from itertools import chain
from operator import mul
from functools import reduce
from math import log10

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

    def score_match(self, record_to_find_match_for, record_potential_match):
        # Find common tokens
        s1 = set(record_to_find_match_for.tokens)
        s2 = set(record_potential_match.tokens)
        common_tokens = s1.intersection(s2)

        # Compute probability
        probs = [self.get_prob(t) for t in common_tokens]
        match_prob = reduce(mul, probs, 1)
        record_potential_match.match_prob = match_prob
        record_potential_match.match_score = self.prob_to_score(match_prob)

    @staticmethod
    def prob_to_score(prob):
        return -(log10(prob))/30

    def generate_probs(self):

        series1 = self.matcher.df_left_processed["_concat_all"]
        series2 = self.matcher.df_right_processed["_concat_all"]
        all_series = pd.concat([series1, series2])

        tokens = list(chain.from_iterable(all_series.apply(str.split)))
        freq_counts = Counter(tokens)
        total_token_count = sum(freq_counts.values())
        probs_dict = {k: freq_counts[k]*1.0/total_token_count for k in freq_counts}

        self.probs_dict = probs_dict
