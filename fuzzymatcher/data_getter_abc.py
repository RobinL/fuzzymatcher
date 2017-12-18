import abc

class DataGetterABC:

    __metaclass__ = abc.ABCMeta

    """
    A DataGetter handles the retrieval of data from df_right (the dataframe in which to search for matches)
    It retrieves a list of potential match ids
    """

    @abc.abstractmethod
    def add_data(self, df_search_within):

        """Adds the data in 'df_search_within'.

        Args:
            df_search_within: The search space i.e. the whole dataset we search within
            to find potential matches

        Returns:
            None
        """



    @abc.abstractmethod
    def get_potential_match_ids_from_record(self, rec_find_match_for):

        """Retrieves lists of potential matches to a record

        Args:
            rec_find_match_for: The record for which we're trying to find a match

        Returns:
            A list of rec_potential_match records which represent the potential matches
            to the rec_find_match_for

        """
