import logging
import pandas as pd
import random
import sqlite3
import copy

from fuzzymatcher.record import Record
from fuzzymatcher.utils import tokens_to_dmetaphones, add_dmetaphone_to_concat_all
log = logging.getLogger(__name__)

class DataGetter:

    """
    A DataGetter handles the retrieval of data from 'df_search_within'
    It retrieves lists of potential matches to a record in 'df_find_match_for'
    in 'df_search_within'
    """

    def __init__(self, return_records_limit=100, search_intensity=100):
        self.return_records_limit = return_records_limit
        self.search_intensity = search_intensity

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
        tkn_po = [t["token"] for t in tkn_po if t["prob"]>0]

        tkn_ms_po = self._tokens_in_df_right_prob_order(rec_left, misspelling=True)
        tkn_ms_po = [t["token"] for t in tkn_ms_po if t["prob"]>0]

        # Start searching with all the terms, then drop them one at a time, starting with the most unusual term
        # TODO: better to scan in blocks e.g. if tokens a b c d go [abcd] [abc] [bcd] [ab] [bc] [cd] [a] [b] [c] [d]
        # TODO: It would make sense to score matches immediately.  Then if best score is high, don't serach further
        # but is best score is low, we can search more intensely

        token_lists = [tkn_po, tkn_po[::-1], tkn_ms_po, tkn_ms_po[::-1]]

        new_matches = []
        for token_list in token_lists:
            for i in range(len(token_list)):
                sub_tokens = token_list[i:]
                new_matches = self._tokens_to_matches(sub_tokens)
                # When we find a match, stop searching
                if len(new_matches) > 0 and len(new_matches) < self.return_records_limit:
                    self._add_matches_to_potential_matches(new_matches, rec_left)
                    break
            if len(rec_left.potential_matches) > 2:
                break

        # If we cannot find a match, search random combinations
        if len(new_matches) == 0 and len(tkn_po) > 1:
            for i in range(self.search_intensity):
                random_tokens = self._get_random_tokens(tkn_po)
                matches = self._tokens_to_matches(random_tokens)
                if len(matches) > 0:
                    break
            self._add_matches_to_potential_matches(matches, rec_left)

    @staticmethod
    def _get_random_tokens(tokens):
        num_tokens = len(tokens)
        n = random.randint(1, num_tokens)
        random_tokens = random.sample(tokens, n)
        return random_tokens

    def _add_matches_to_potential_matches(self, matches, rec_left):
        for match in matches:
            right_id = match[0]
            if right_id not in rec_left.potential_matches:
                scored_potential_match = self.matcher.scorer.score_match(rec_left.record_id, right_id)
                rec_left.potential_matches[right_id] = scored_potential_match


    def _tokens_to_matches(self, tokens, misspelling = False):

        get_records_sql = """
            SELECT * FROM fts_target WHERE {} MATCH '{}' limit {};
            """

        # This fails if the special tokens 'and' or 'or' are in fts string!  See issue 35!
        tokens_to_remove = ["AND", "OR"]
        tokens = [t for t in tokens if t not in tokens_to_remove]
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

    def _remove_freq_zero_tokens(self, tokens):
        return [t for t in tokens if self.matcher.scorer.get_prob_right(t) > 0]

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

        tokens_list.sort(key=lambda x: x["prob"])

        return tokens_list
