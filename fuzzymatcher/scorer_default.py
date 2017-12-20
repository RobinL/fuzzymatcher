# -*- coding: utf-8 -*-
import pandas as pd
from collections import Counter
from itertools import chain, product
from operator import mul
from functools import reduce
from math import log10
from functools import lru_cache

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

    def get_prob(self, token, field, left_right, misspelling=False):
        """
        Get probability given field and token
        """

        try:
            if not misspelling and left_right == "left":
                return self.left_field_token_probs_dict[field][token]

            if not misspelling and left_right == "right":
                return self.right_field_token_probs_dict[field][token]

            if misspelling and left_right == "left":
                return self.left_field_misspelling_probs_dict[field][token]

            if misspelling and left_right == "right":
                return self.right_field_misspelling_probs_dict[field][token]
        except KeyError:
            return None

    @lru_cache(maxsize=int(1e6))
    def score_match(self, record_left_id, record_right_id):

        record_left = self.matcher.left_records[record_left_id]
        record_right = self.matcher.right_records[record_right_id]
        # Need to find common tokens, and get their probabilities
        fields_left = record_left.fields

        prob = 1
        for f_left in fields_left:
            p = self._field_to_prob(f_left, record_left, record_right)
            prob = p * prob

        match_score = self.prob_to_score(prob)
        return {"match_prob" : prob, "match_score": match_score, "record_right": record_right}


    def _field_to_prob(self, field_left, record_left, record_right):

        field_right = self.matcher.left_to_right_lookup[field_left]

        tokens_left = set(record_left.clean_token_dict[field_left])
        tokens_right = set(record_right.clean_token_dict[field_right])

        matching_tokens = tokens_left.intersection(tokens_right)
        unmatching_tokens_left = tokens_left.difference(tokens_right)
        unmatching_tokens_right = tokens_right.difference(tokens_left)

        prob_matching = self._get_prob_matching(matching_tokens, field_right)

        prob_unmatching1 = self._get_prob_unmatching(unmatching_tokens_left, tokens_right, field_right, field_left)
        prob_unmatching2 = self._get_prob_unmatching(unmatching_tokens_right, tokens_left, field_right, field_left)

        tokens_alt_left = set(record_left.token_misspelling_dict[field_left])
        tokens_alt_right = set(record_right.token_misspelling_dict[field_right])
        matching_tokens_alt = tokens_alt_left.intersection(tokens_alt_right)
        prob_matching_alt = self._get_prob_matching(matching_tokens_alt, field_right, misspelling=True)

        prob = prob_matching * prob_unmatching1 * prob_unmatching2 * prob_matching_alt

        return prob

    def _get_prob_matching(self, tokens, f_right, misspelling=False):
        prob = 1
        for t in tokens:
            p = self.get_prob(t,f_right,"right", misspelling)
            prob = p * prob
        return prob

    def _get_prob_unmatching(self, unmatching_tokens, record_tokens, field_right, field_left):
        # If the unmatching token is not a misspelling, then undo its probability
        prob = 1
        for umt in unmatching_tokens:
            if not self._is_misspelling_of_one(umt, record_tokens):
                p = self.get_prob(umt,field_right,"right")
                if p is None: # If this token never appears on the right, how often does it appear on the left
                    p = self.get_prob(umt,field_left,"left")
                prob = p * prob

        prob = Scorer._adjust_prob_towards_one(prob)
        return 1/prob

    def _is_misspelling_of_one(self, token, token_list):
        for t in token_list:
            if self.matcher.token_comparison.is_mispelling(token, t):
                return True
        return False

    def get_token_lists_by_field(self, recordsdict, attribute):
        token_lists_by_field = {}
        key = next(iter(recordsdict))
        fields = recordsdict[key].fields
        for f in fields:
            token_lists_by_field[f] = []

        for key, this_record in recordsdict.items():
            for f in fields:
                tokens = getattr(this_record, attribute)[f]
                token_lists_by_field[f].extend(tokens)

        return token_lists_by_field

    def field_tokens_to_prob(self, field_tokens):
        ft = field_tokens
        for key, value in ft.items():
            counts = Counter(value)
            count_sum = sum(counts.values())
            counts = {k: v/count_sum for k,v in counts.items()}
            ft[key] = counts
        return ft

    def _generate_probs(self):
        left_field_tokens =  self.get_token_lists_by_field(self.matcher.left_records, "clean_token_dict")
        self.left_field_token_probs_dict = self.field_tokens_to_prob(left_field_tokens)

        right_field_tokens =  self.get_token_lists_by_field(self.matcher.right_records, "clean_token_dict")
        self.right_field_token_probs_dict = self.field_tokens_to_prob(right_field_tokens)

        left_field_tokens =  self.get_token_lists_by_field(self.matcher.left_records, "token_misspelling_dict")
        self.left_field_misspelling_probs_dict = self.field_tokens_to_prob(left_field_tokens)

        right_field_tokens =  self.get_token_lists_by_field(self.matcher.right_records, "token_misspelling_dict")
        self.right_field_misspelling_probs_dict = self.field_tokens_to_prob(right_field_tokens)

    @staticmethod
    def prob_to_score(prob):
        return -(log10(prob))/30

    @staticmethod
    def _adjust_prob_towards_one(initial_prob, amount = 2):
        return initial_prob
