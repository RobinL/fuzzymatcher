from fuzzymatcher.data_preprocessor_default import DataPreprocessor
from fuzzymatcher.data_getter_sqlite import DataGetter
from fuzzymatcher.scorer_default import Scorer

from fuzzymatcher.matcher import Matcher

import pandas as pd
import importlib


def link_table(df_left,
            df_right,
            left_on,
            right_on,
            left_word_cols = None,
            right_word_cols = None,
            left_id_col = None,
            right_id_col = None):

    dp = DataPreprocessor()
    dg = DataGetter()
    s = Scorer()

    m = Matcher(dp, dg, s)

    m.add_data(df_left, df_right, left_on, right_on, left_word_cols, right_word_cols, left_id_col, right_id_col)

    m.match_all()

    return m.link_table