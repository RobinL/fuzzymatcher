# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter
from itertools import chain, product
from operator import mul
from functools import reduce
from math import log10

import logging
log = logging.getLogger(__name__)

from fuzzymatcher.utils import add_dmetaphones_to_col, is_mispelling, convert_series_to_dmetaphones, tokens_to_dmetaphones

class Scorer:

    """
    A DataPreprocessor is responsible for ingesting df_left (the dataframe containing the records we
    want to find matches for) and df_right (the dataframe we want to search for potential matches)
    and applying preprocessing stages like normalisation to make matching easier.
    """

    def add_data(self, matcher):
        self.matcher = matcher
        self._generate_probs()

    def get_prob_left(self, token):
        return self.probs_dict_left.get(token, 0)

    def get_prob_right(self, token):
        return self.probs_dict_right.get(token, 0)

    def score_match(self, record_to_find_match_for, record_potential_match):
        # Find common tokens
        s1 = set(record_to_find_match_for.tokens)

        # Add dmetaphones to the left record (already added to right record on creation of FTS table)
        # TODO: More thoroughly separate out dmetaphones from everything else

        s1_dmp = tokens_to_dmetaphones(s1)
        s1 = s1.union(s1_dmp)

        s2 = set(record_potential_match.tokens)
        common_tokens = s1.intersection(s2)

        # Compute probability.  Score based on the rarity of the token in the search space (df_right)
        # (This seems to make more sense than the rarity of the token in df_left)
        probs = [self.get_prob_right(t) for t in common_tokens]
        match_prob = reduce(mul, probs, 1)

        # Looking at the tokens which do not match, do any of them look like misspellings?
        # If so, ignore them.
        unique_tokens_left = s1.difference(s2)
        unique_tokens_right = s2.difference(s1)

        combos = product(unique_tokens_left, unique_tokens_right)

        mispelling_tokens_left = set()
        mispelling_tokens_right = set()
        for c in combos:
            if is_mispelling(c[0], c[1]):
                mispelling_tokens_left.add(c[0])
                mispelling_tokens_right.add(c[1])

        unique_tokens_left = unique_tokens_left.difference(mispelling_tokens_left)
        unique_tokens_right = unique_tokens_right.difference(mispelling_tokens_right)

        # If there are tokens in record_to_find_match for which aren't in record_potential_match
        # then this should reduce the score, especially if those tokens are uncommon

        for t in unique_tokens_left:
            prob_adjustment = self.get_prob_left(t)
            match_prob = self._adjust_prob_towards_one(match_prob, prob_adjustment)

        for t in unique_tokens_right:
            prob_adjustment = self.get_prob_right(t)
            match_prob = self._adjust_prob_towards_one(match_prob, prob_adjustment)

        record_potential_match.match_prob = match_prob
        record_potential_match.match_score = self.prob_to_score(match_prob)

    @staticmethod
    def series_to_prob_dict(series):
        tokens = list(chain.from_iterable(series.apply(str.split)))
        freq_counts = Counter(tokens)
        total_token_count = sum(freq_counts.values())
        probs_dict = {k: freq_counts[k]*1.0/total_token_count for k in freq_counts}
        return probs_dict

    @staticmethod
    def prob_to_score(prob):
        return -(log10(prob))/30

    def _generate_probs(self):

        series_left = self.matcher.df_left_processed["_concat_all"]
        series_left_dmp = convert_series_to_dmetaphones(series_left)
        series_left_all = pd.concat([series_left, series_left_dmp])
        self.probs_dict_left = self.series_to_prob_dict(series_left_all)

        series_right = self.matcher.df_right_processed["_concat_all"]
        series_right_dmp = convert_series_to_dmetaphones(series_right)
        series_right_all = pd.concat([series_right, series_right_dmp])
        self.probs_dict_right = self.series_to_prob_dict(series_right_all)

    @staticmethod
    def _adjust_prob_towards_one(initial_prob, prob):
        return initial_prob * 1/prob
