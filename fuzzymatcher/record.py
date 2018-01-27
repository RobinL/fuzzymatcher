from fuzzymatcher.utils import tokens_to_dmetaphones
import pandas as pd
import random
import re

class Record:
    """
    The 'record' objects represents a row of a dataset.
    A row is represented as a dictionary called 'field dict', whose keys are the column (field) names
    and whose values are the column values.

    The record object has methods to clean (homogenise) and tokenise these column values.
    The record object also has a dictionary similar to field dict that contains token misspellings
    """

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
        self.potential_matches = {} # A dictionary with right_id as key
        self.best_match_score = -float("inf")

    def find_and_score_potential_matches(self):
        # Each left_record has a list of left_record ids
        self.matcher.data_getter.get_potential_match_ids_from_record(self)

    def get_link_table_rows(self):
        rows = []

        for k, v in self.potential_matches.items():
            row = {}
            row["__id_left"] = self.record_id
            row["__id_right"] = v["record_right"].record_id
            row["__score"] = v["match_score"]
            # TODO
            #row["__score"] = p.match_prob
            rows.append(row)

        if len(self.potential_matches.items()) == 0: #If there is no potential match, still want a row in link table
            row = {}
            row["__id_left"] = self.record_id
            row["__id_right"] = None
            row["__score"] = None
            rows.append(row)



        rows.sort(key=lambda r: r['__score'], reverse=True)

        for i, r in enumerate(rows):
            r["__rank"] = i + 1

        return rows


