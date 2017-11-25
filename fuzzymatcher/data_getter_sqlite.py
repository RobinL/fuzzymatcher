import sqlite3
from fuzzymatcher.record import Record


class DataGetter:

    """
    A DataGetter handles the retrieval of data from 'df_search_within'
    It retrieves lists of potential matches to a record in 'df_find_match_for'
    in 'df_search_within'
    """

    def __init__(self):
        pass

    def add_data(self, matcher):

        """Adds the data in 'matcher.df_search_within'.

        Args:
            df_search_within: The search space i.e. the whole dataset we search within
            to find potential matches

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


    def get_potential_matches_from_record(self, rec_find_match_for):

        """Retrieves lists of potential matches to a record

        Args:
            rec_find_match_for: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """

        get_records_sql = """
            SELECT * FROM fts_target WHERE fts_target MATCH '{}' limit {};
            """

        get_records_sql = get_records_sql.format("james john", "100")

        get_records_sql = "select * from fts_target"
        cur = self.con.cursor()
        cur.execute(get_records_sql)
        results = cur.fetchall()

        potential_matches = []
        for r in results:
            potential_matches.append(Record(r[0], r[1], self.matcher))

        return potential_matches

