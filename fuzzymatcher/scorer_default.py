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

    def get_prob_left(self, token, field):
        """
        Get probability given field and token
        """
        return self.probs_dict_left.get(token, 0)

    def get_prob_right(self, token):
        return self.probs_dict_right.get(token, 0)

    def score_match(self, record_to_find_match_for, record_potential_match):
        pass

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
    def _adjust_prob_towards_one(initial_prob, prob):
        return initial_prob * 1/prob
