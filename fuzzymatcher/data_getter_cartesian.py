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

        self.matcher = matcher

    def get_potential_match_ids_from_record(self, rec_left):

        """Retrieves lists of potential matches to a record

        Args:
            rec_find_match_for: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """

        for record_right_id ,record_right in self.matcher.right_records.items():
            scored_potential_match = self.matcher.scorer.score_match(rec_left.record_id, record_right_id)
            rec_left.potential_matches[record_right_id] = scored_potential_match

