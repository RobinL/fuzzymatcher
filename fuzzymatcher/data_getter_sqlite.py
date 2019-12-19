import logging
import pandas as pd
import random
import sqlite3
import copy
from functools import lru_cache

from fuzzymatcher.record import Record
from fuzzymatcher.utils import tokens_to_dmetaphones, add_dmetaphone_to_concat_all
log = logging.getLogger(__name__)

class DataGetter:

    """
    A DataGetter handles the retrieval of data from 'df_search_within'
    It retrieves lists of potential matches to a record in 'df_find_match_for'
    in 'df_search_within'
    """

    def __init__(self, return_records_limit=50, search_intensity=100, found_score_threshold = 0, found_num_records_threshold = 200):
        self.return_records_limit = return_records_limit
        self.search_intensity = search_intensity
        self.found_score_threshold = found_score_threshold
        self.found_num_records_threshold = found_num_records_threshold

    def add_data(self, matcher):

        """Adds the data in 'matcher.df_search_within' to a sqlite database
        and create a connection to the database to be used by the data getter
        Also registers the match object on the datagetter.

        Args:
            matcher.  The matcher object

        Returns:
            None
        """

        self.matcher = matcher

        # Turn right_records into strings and add to db
        rows = []
        for key, record in matcher.right_records.items():
            row = {}
            row["id"] = record.record_id
            row["_concat_all"] = record.clean_string
            row["_concat_all_alternatives"] = record.get_concat_string(record.token_misspelling_dict)
            rows.append(row)

        df = pd.DataFrame(rows)
        df = df[["id", "_concat_all", "_concat_all_alternatives"]]

        con = sqlite3.connect(':memory:', timeout=0.3)

        df.to_sql("df_right_processed", con, index=False)
        sql = """
                 CREATE VIRTUAL TABLE fts_target
                 USING fts4({} TEXT, _concat_all TEXT, _concat_all_alternatives TEXT);
              """.format(matcher.right_id_col)
        con.execute(sql)
        con.execute("INSERT INTO fts_target SELECT * FROM df_right_processed")

        self.con = con

        # TODO:  Compute the min, max, average number of tokens in a record to help optimise the search


    def get_potential_match_ids_from_record(self, rec_left):

        """Retrieves lists of potential matches to a record

        Args:
            rec_left: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_left

        """

        tkn_po = self._tokens_in_df_right_prob_order(rec_left)

        # No point in running FTS using a token we know isn't in df_right


        tkn_ms_po = self._tokens_in_df_right_prob_order(rec_left, misspelling=True)


        # Start searching with all the terms, then drop them one at a time, starting with the most unusual term
        token_lists = [tkn_po, tkn_ms_po]

        for token_list in token_lists:
            self._search_specific_to_general_single(token_list, rec_left)
            if not self._found_enough_matches(rec_left):
                self._search_specific_to_general_band(token_list, rec_left)
            if self._found_enough_matches(rec_left):
                break

        # If we cannot find a match, search random combinations
        if not self._found_good_match(rec_left):
            matches = self._search_random(tkn_po)
            self._add_matches_to_potential_matches(matches, rec_left)

    @staticmethod
    def _get_random_tokens(tokens):
        num_tokens = len(tokens)
        if num_tokens == 0:
            return ()
        n = random.randint(1, num_tokens)
        random_tokens = random.sample(tokens, n)
        return tuple(random_tokens)

    def _search_specific_to_general_single(self, token_list, rec_left):

        for i in range(len(token_list)):
            sub_tokens = token_list[i:]
            new_matches = self._tokens_to_matches(tuple(sub_tokens))

            self._add_matches_to_potential_matches(new_matches, rec_left)
            if self._found_enough_matches(rec_left):
                return

    def _search_specific_to_general_band(self, tokens, rec_left):
        """
        Search in blocks e.g. if tokens a b c d go [abcd] [abc] [bcd] [ab] [bc] [cd] [a] [b] [c] [d]
        """
        num_tokens = len(tokens)
        for band_size in range(num_tokens, 0,-1):
            take = num_tokens - band_size + 1
            for start_pos in range(0, take):
                end_pos = start_pos + band_size
                search_tokens = tokens[start_pos:end_pos]
                new_matches = self._tokens_to_matches(tuple(search_tokens))
                self._add_matches_to_potential_matches(new_matches, rec_left)
                if self._found_good_match(rec_left):
                    return
                if len(rec_left.potential_matches) > self.found_num_records_threshold:
                    return

    def _found_good_match(self, rec_left):
        return rec_left.best_match_score > self.found_score_threshold

    def _found_enough_matches(self, rec_left):
        if rec_left.best_match_score > self.found_score_threshold:
            return True
        if len(rec_left.potential_matches) > self.found_num_records_threshold:
            return True
        return False


    def _search_random(self, token_list):
        matches = []
        prev_random_tokens = set()
        for i in range(self.search_intensity):
            random_tokens = self._get_random_tokens(token_list)
            if random_tokens not in prev_random_tokens:
                prev_random_tokens.add(random_tokens)
                matches = self._tokens_to_matches(random_tokens)
            if len(matches) > 0:
                break
        return matches

    def _add_matches_to_potential_matches(self, matches, rec_left):
        for match in matches:
            right_id = match[0]
            if right_id not in rec_left.potential_matches:
                scored_potential_match = self.matcher.scorer.score_match(rec_left.record_id, right_id)
                rec_left.potential_matches[right_id] = scored_potential_match
                if rec_left.best_match_score < scored_potential_match["match_score"]:
                   rec_left.best_match_score = scored_potential_match["match_score"]

    @lru_cache(maxsize=int(1e6))
    def _tokens_to_matches(self, tokens, misspelling = False):

        get_records_sql = """
            SELECT * FROM fts_target WHERE {} MATCH '{}' limit {};
            """

        # This fails if the special tokens 'and' or 'or' are in fts string!  See issue 35!
        tokens_to_escape = ["AND", "OR", "NEAR", "NOT"]

        def escape_token(t):
            # return t
            if t in tokens_to_escape:
                return '"' + t + '"'
            else:
                return t


        tokens = [escape_token(t) for t in tokens]

        fts_string = " ".join(tokens)


        if misspelling:
            table_name = "_concat_all_alternatives"
        else:
            table_name = "_concat_all"

        sql = get_records_sql.format(table_name, fts_string, self.return_records_limit)


        cur = self.con.cursor()
        cur.execute(sql)
        results = cur.fetchall()

        return results


    def _tokens_in_df_right_prob_order(self, rec_to_find_match_for, misspelling = False):
        # Problem here is that field names are different in left and right
        fields = rec_to_find_match_for.fields
        if misspelling:
            token_dict = rec_to_find_match_for.token_misspelling_dict
        else:
            token_dict = rec_to_find_match_for.clean_token_dict
        get_prob = self.matcher.scorer.get_prob

        tokens_list = []
        for field, tokens in token_dict.items():
            for t in tokens:
                translated_field = self.matcher.left_to_right_lookup[field]
                prob = get_prob(t,translated_field,"right",misspelling)
                tokens_list.append({"token": t, "prob": prob})

        tokens_list = [t for t in tokens_list if t["prob"] is not None]
        tokens_list.sort(key=lambda x: x["prob"])
        tokens_list = [t["token"] for t in tokens_list]
        return tokens_list
