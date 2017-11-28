# -*- coding: utf-8 -*-

"""
Tests
"""

import datetime
import json
import pandas as pd
import subprocess
import unittest

from fuzzymatcher import link_table
from fuzzymatcher.data_getter_cartesian import DataGetterCartesian
from fuzzymatcher.matcher import Matcher

def link_table_percentage_correct(link_table):
    lt = link_table.copy()
    lt = lt[lt["match_rank"] == 1]
    lt["__id_left"] = lt["__id_left"].str.replace("_left", "")
    lt["__id_right"] = lt["__id_right"].str.replace("_right", "")
    lt["link_correct"] = (lt["__id_left"] == lt["__id_right"])

    return lt["link_correct"].sum()/len(lt)

class DatagetterAccuracy(unittest.TestCase):
    """
    These tests actually run accurancy analysis of the results
    They're not pass fail but they log how well the matcher is doing
    """

    dg = DataGetterCartesian()
    m = Matcher(data_getter = dg)

    df_left = pd.read_csv("tests/data/left_3.csv")
    df_right = pd.read_csv("tests/data/right_3.csv")

    on = ["first_name", "surname", "dob", "city"]

    m.add_data(df_left, df_right, on, on)

    m.match_all()
    lt = m.get_formatted_link_table()

    cartesian_perc = link_table_percentage_correct(lt)


    lt2 = link_table(df_left, df_right, on, on)
    sqlite_perc = link_table_percentage_correct(lt2)

    process = subprocess.Popen("git describe --always", stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    commit_hash = output.decode("utf-8").replace("\n", "")


    this_record = {}
    this_record["datetime"] = datetime.datetime.now().isoformat()
    this_record["commit_hash"] = commit_hash
    this_record["datagetter_cartesian"] = cartesian_perc
    this_record["datagetter_sqlite"] = sqlite_perc

    with open("tests/datagetter_performance.txt", "a") as myfile:
        myfile.writelines(json.dumps(this_record) + "\n")
