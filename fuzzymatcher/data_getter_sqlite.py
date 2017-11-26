import sqlite3
from fuzzymatcher.record import Record
import random

class DataGetter:

    """
    A DataGetter handles the retrieval of data from 'df_search_within'
    It retrieves lists of potential matches to a record in 'df_find_match_for'
    in 'df_search_within'
    """

    def __init__(self, return_records_limit=100, search_intensity=100, cartesian = False):
        self.return_records_limit = return_records_limit
        self.search_intensity = search_intensity
        self.cartesian = cartesian

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

        con = sqlite3.connect(':memory:')
        matcher.df_right_processed.to_sql("df_right_processed", con, index=False)
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

        # If the user's asked for the cartesian product then retrieve all records from df_right
        if self.cartesian:
            matches = self._cartesian_matches()
            potential_matches = []
            for m in matches:
                potential_matches.append(Record(m[0], m[1], self.matcher))
            return potential_matches

        tokens_prob_order = rec_find_match_for.tokens_prob_order
        # Start searching with all the terms, then drop them one at a time, starting with the most unusual term
        for i in range(len(tokens_prob_order)):
            sub_tokens = tokens_prob_order[i:]
            matches = self._tokens_to_matches(sub_tokens)
            # When we find a match, stop searching
            if len(matches) > 0:
                break

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

    def _cartesian_matches(self):
        sql = """
            SELECT * FROM fts_target;
            """
        cur = self.con.cursor()
        cur.execute(sql)
        results = cur.fetchall()

        return results
