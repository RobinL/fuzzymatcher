import random
import sqlite3

from fuzzymatcher.record import Record
from fuzzymatcher.data_getter_abc import DataGetterABC

class DataGetterCartesian(DataGetterABC):

    """
    The DataGetter class handles the retrieval of record_ids from 'df_right'

    This Cartesian datagetter is the simplest, most thorough, but least efficient implementation
    where every record_id in 'df_right' is returned, compared and scored against 'df_left', leading to n^2 complexity.

    """

    def add_data(self, matcher):

        """
        Registers the matcher on the datagetter so the datagetter can manipulate the matcher object

        Args:
            matcher.  The matcher object

        Returns:
            None
        """

        self.matcher = matcher

    def get_potential_match_ids_from_record(self, rec_left):

        """Retrieves lists of potential matches to a record

        Args:
            rec_left: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """

        for record_right_id ,record_right in self.matcher.right_records.items():
            scored_potential_match = self.matcher.scorer.score_match(rec_left.record_id, record_right_id)
            rec_left.potential_matches[record_right_id] = scored_potential_match

