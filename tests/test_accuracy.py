# -*- coding: utf-8 -*-

"""
Tests
"""

import datetime
import json
import pandas as pd
import subprocess
from timeit import default_timer as timer
import unittest



from fuzzymatcher import link_table, fuzzy_left_join
from fuzzymatcher.data_getter_cartesian import DataGetterCartesian
from fuzzymatcher.matcher import Matcher

def get_commit_hash():
    process = subprocess.Popen("git describe --always", stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    commit_hash = output.decode("utf-8").replace("\n", "")
    return commit_hash

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

    def test_data_1000(self):

        m = Matcher()

        df_left = pd.read_csv("tests/data/left_4.csv")
        df_right = pd.read_csv("tests/data/right_4.csv")

        on = ["first_name", "surname", "dob", "city"]

        m.add_data(df_left, df_right, on, on)

        start = timer()
        m.match_all()
        lt = m.get_formatted_link_table()
        end = timer()
        time_taken = end - start
        sqlite_perc = link_table_percentage_correct(lt)

        this_record = {}
        this_record["datetime"] = datetime.datetime.now().isoformat()
        this_record["commit_hash"] = get_commit_hash()
        this_record["datagetter_cartesian"] = "NA"
        this_record["datagetter_sqlite"] = sqlite_perc
        this_record["test_type"] = "left_4"
        this_record["time_taken"] = time_taken

        with open("tests/datagetter_performance.txt", "a") as myfile:
            myfile.writelines(json.dumps(this_record) + "\n")

    def test_data_100(self):
        dg = DataGetterCartesian()
        m = Matcher(data_getter = dg)

        df_left = pd.read_csv("tests/data/left_3.csv")
        df_right = pd.read_csv("tests/data/right_3.csv")

        on = ["first_name", "surname", "dob", "city"]

        m.add_data(df_left, df_right, on, on)

        start = timer()
        m.match_all()
        lt = m.get_formatted_link_table()
        end = timer()
        time_taken = end - start

        cartesian_perc = link_table_percentage_correct(lt)

        lt2 = link_table(df_left, df_right, on, on)
        sqlite_perc = link_table_percentage_correct(lt2)

        this_record = {}
        this_record["datetime"] = datetime.datetime.now().isoformat()
        this_record["commit_hash"] = get_commit_hash()
        this_record["datagetter_cartesian"] = cartesian_perc
        this_record["datagetter_sqlite"] = sqlite_perc
        this_record["test_type"] = "left_3"
        this_record["time_taken"] = time_taken

        with open("tests/datagetter_performance.txt", "a") as myfile:
            myfile.writelines(json.dumps(this_record) + "\n")

    def test_la_data(self):
        ons = pd.read_csv("tests/data/las_ons.csv")
        os = pd.read_csv("tests/data/las_os.csv")

        start = timer()
        df_joined = fuzzy_left_join(ons, os, left_on = ["lad16nm"], right_on = ["name"])
        end = timer()
        time_taken =  end - start

        rename = {"lad16cd": "ons_code", "code": "os_code", "lad16nm": "ons_name", "name": "os_name"}
        df_joined = df_joined.rename(columns=rename)
        col_order = ["best_match_score", "ons_name", "os_name", "ons_code", "os_code"]

        num_records = len(df_joined)
        correct_binary = (df_joined["ons_code"] == df_joined["os_code"])
        perc_correct = correct_binary.sum()/num_records

        this_record = {}
        this_record["datetime"] = datetime.datetime.now().isoformat()
        this_record["commit_hash"] = get_commit_hash()
        this_record["perc_correct"] = perc_correct
        this_record["test_type"] = "local_authority"
        this_record["time_taken"] = time_taken

        with open("tests/realexample_performance.txt", "a") as myfile:
            myfile.writelines(json.dumps(this_record) + "\n")
