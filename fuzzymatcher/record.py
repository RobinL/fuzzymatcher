import pandas as pd
import random

class Record:

    def __init__(self, record_id, record_string, matcher):
        self.record_id = record_id
        self.record_string = record_string
        self.matcher = matcher
        self.tokens = self.tokenise(record_string)
        self.tokens_prob_order = self.in_prob_order_asc()  #QUESTION:  The method could just set this property

    @staticmethod
    def tokenise(record_string):
        return record_string.split(" ")

    def in_prob_order_asc(self):
        return sorted(self.tokens, key=lambda x: self.matcher.scorer.get_prob(x))

    def get_n_tokens_random_order():
        pass

    def get_random_tokens(self):
        num_tokens = len(self.tokens)
        n = random.randint(1, num_tokens)
        random_tokens = random.sample(self.tokens, n)
        return random_tokens

    def __repr__(self):
        return "ID: {}, Record String: {}".format(self.record_id, self.record_string)


class RecordToMatch(Record):

    def __init__(self, *args, **kwargs):
        Record.__init__(self, *args, **kwargs)
        self.potential_matches = None

    def get_potential_matches(self):
        return self.matcher.data_getter.get_potential_matches_from_record(self)

    def find_and_score_potential_matches(self):
        self.potential_matches = self.get_potential_matches()

        for p in self.potential_matches:
            self.matcher.scorer.score_match(self, p)

    def get_link_table_rows(self):
        rows = []
        for p in self.potential_matches:
            row = {}
            row["__id_left"] = self.record_id
            row["__id_right"] = p.record_id
            row["__score"] = p.match_score
            rows.append(row)

        rows.sort(key=lambda r: r['__score'])

        for i, r in enumerate(rows):
            r["__rank"] = i + 1

        return rows



class RecordPotentialMatch(Record):
    # Need to add match score

    def __init__(self, *args, **kwargs):
        Record.__init__(self, *args, **kwargs)
        self.match_score = None