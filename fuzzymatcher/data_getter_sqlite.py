import logging
import random
import sqlite3

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

        # Create dmetaphone column

        con = sqlite3.connect(':memory:', timeout=0.05)
        df = matcher.df_right_processed.copy()
        add_dmetaphone_to_concat_all(df)

        df.to_sql("df_right_processed", con, index=False)
        sql = """
                 CREATE VIRTUAL TABLE fts_target
                 USING fts4({} TEXT, _concat_all TEXT);
              """.format(matcher.right_id_col)
        con.execute(sql)
        con.execute("INSERT INTO fts_target SELECT * FROM df_right_processed")

        self.con = con

        # TODO:  Compute the min, max, average number of tokens in a record to help optimise the search


    def get_potential_matches_from_record(self, rec_find_match_for):

        """Retrieves lists of potential matches to a record

        Args:
            rec_find_match_for: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """

        tkn_po = rec_find_match_for.tokens_prob_order
        tkn_dm = rec_find_match_for.dmetaphones_prob_order

        # Start searching with all the terms, then drop them one at a time, starting with the most unusual term

        token_lists = [tkn_po, tkn_po[::-1], tkn_dm, tkn_dm[::-1]]

        matches_counter = 0
        matches = []
        for token_list in token_lists:
            for i in range(len(token_list)):
                sub_tokens = token_list[i:]
                # log.debug(" ".join(sub_tokens))
                matches = self._tokens_to_matches(sub_tokens)

                # When we find a match, stop searching
                if len(matches) > 0 and len(matches) < self.return_records_limit:
                    matches.extend(matches)
                    matches_counter += 1
                    break
            if matches_counter == 2:
                break

        # Dedupe matches
        matches = set(matches)

        # If we cannot find a match, search random combinations
        if len(matches) == 0:
            for i in range(self.search_intensity):
                matches = self._tokens_to_matches(rec_find_match_for.get_random_tokens())
                if len(matches) > 0:
                    break

        potential_matches = []
        for m in matches:
            potential_matches.append(Record(m[0], m[1], self.matcher))

        return potential_matches

    def _tokens_to_matches(self, tokens):

        get_records_sql = """
            SELECT * FROM fts_target WHERE fts_target MATCH '{}' limit {};
            """
        fts_string = " ".join(tokens)
        sql = get_records_sql.format(fts_string, self.return_records_limit)
        cur = self.con.cursor()
        cur.execute(sql)
        results = cur.fetchall()

        return results
