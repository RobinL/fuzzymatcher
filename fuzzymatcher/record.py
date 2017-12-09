from fuzzymatcher.utils import tokens_to_dmetaphones
import pandas as pd
import random
import re

class Record:

    def __init__(self, field_dict, record_id, matcher):
        self.orig_field_dict = field_dict
        self.record_id = record_id
        self.matcher = matcher

        self.fields = list(field_dict.keys())
        self.clean_token_dict = Record.get_tokenised_field_dict(field_dict)
        self.clean_string = Record.get_concat_string(self.clean_token_dict)

        self.token_misspelling_dict = self.get_tokenised_misspelling_dict()



    def __repr__(self):
        return self.clean_string

    def get_tokenised_misspelling_dict(self):
        get_misspellings = self.matcher.token_comparison.get_misspellings

        misspellings_dict = {}
        for field, tokens in self.clean_token_dict.items():
            misspelling_tokens = []
            for t in tokens:
                misspelling_tokens.extend(get_misspellings(t))
            misspellings_dict[field] = misspelling_tokens
        return misspellings_dict

    @staticmethod
    def field_to_string(value):
        return str(value)

    @staticmethod
    def get_tokenised_field_dict(field_dict):
        cleaned_token_dict = {}
        for key, value in field_dict.items():
            value = Record.field_to_string(value)
            value = value.upper()

            value = value.replace("'", " ")
            value = re.sub('[^\w\s]',' ', value)
            value = re.sub('\s{2,100}',' ', value)
            value = value.strip()

            cleaned_token_dict[key] = value.split(" ")
        return cleaned_token_dict

    @staticmethod
    def get_concat_string(token_dict):
        tokens = []
        for key, value in token_dict.items():
            tokens.extend(value)
        return " ".join(tokens)

class RecordToMatch(Record):

    def __init__(self, *args, **kwargs):
        Record.__init__(self, *args, **kwargs)
        self.potential_matches = None


class RecordPotentialMatch(Record):

    def __init__(self, *args, **kwargs):
        Record.__init__(self, *args, **kwargs)
        self.match_score = None