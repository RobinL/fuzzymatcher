import random
import sqlite3

from fuzzymatcher.record import Record
from fuzzymatcher.data_getter_abc import DataGetterABC

class DataGetterCartesian(DataGetterABC):

    """
    A DataGetter handles the retrieval of data from 'df_search_within'
    It retrieves lists of potential matches to a record in 'df_find_match_for'
    in 'df_search_within'
    """

    def add_data(self, matcher):

        """Adds the data in 'matcher.df_search_within' to a sqlite database
        and create a connection to the database to be used by the data getter
        Also registers the match object on the datagetter.

        Args:
            matcher.  The matcher object

        Returns:
            None
        """

        self.potential_matches = []
        for r in matcher.df_right_processed.iterrows():
            row = r[1]
            self.potential_matches.append(Record(row[0], row[1], matcher))

    def get_potential_matches_from_record(self, rec_find_match_for):

        """Retrieves lists of potential matches to a record

        Args:
            rec_find_match_for: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """

        return self.potential_matches