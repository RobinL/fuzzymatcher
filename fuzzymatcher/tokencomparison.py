from functools import lru_cache
from metaphone import doublemetaphone
from fuzzywuzzy import fuzz

class TokenComparison:

    def __init__(self, fuzz_ratio_threshold = 80):
        self.fuzz_ratio_threshold = fuzz_ratio_threshold

    @lru_cache(maxsize=int(1e6))
    def get_misspellings(self, token):
        """
        Must return a list of misspellings
        If there are no misspellings, just return a list of length 0
        """
        misspellings = doublemetaphone(token)
        misspellings = [t for t in misspellings if t != ""]
        return misspellings

    @lru_cache(maxsize=int(1e6))
    def is_mispelling(self, token1, token2):
        mis_t1 = set(self.get_misspellings(token1))
        mis_t2 = set(self.get_misspellings(token2))
        common = mis_t1.intersection(mis_t2).difference({''})  # Difference in case '' included in tokens

        if len(common) > 0:
            return True

        # Misspellings only really make sense if the tokens are words not numbers
        if token1.isalpha() and token2.isalpha():
            if fuzz.ratio(token1, token2) > self.fuzz_ratio_threshold:
                return True

        return False

