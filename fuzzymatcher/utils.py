from metaphone import doublemetaphone
from fuzzywuzzy.fuzz import ratio

def tokens_to_dmetaphones(tokens):
    new_tokens = []
    for t in tokens:
        dmp = doublemetaphone(t)
        if dmp[0] == '':
            pass
        elif dmp[1] == '':
            new_tokens.append(dmp[0])
        else:
            new_tokens.extend(dmp)

    new_tokens = [t.strip() for t in new_tokens]
    return new_tokens

def add_dmetaphones_to_col(x):
    tokens = x.split(" ")
    new_tokens = tokens_to_dmetaphones(tokens)
    tokens.extend(new_tokens)
    return " ".join(tokens)

def add_dmetaphone_to_concat_all(df):
    df["_concat_all"] =  df["_concat_all"].apply(add_dmetaphones_to_col)

def convert_tokens_to_dmetaphones(x):
    tokens = x.split(" ")
    new_tokens = tokens_to_dmetaphones(tokens)
    return " ".join(new_tokens)

def convert_series_to_dmetaphones(series):
    return series.apply(convert_tokens_to_dmetaphones)

def is_mispelling(token_left, token_right):

    dml = set(doublemetaphone(token_left))
    dmr = set(doublemetaphone(token_right))

    if len(dml.intersection(dmr).difference({''})) > 0:
        return True

    if ratio(token_left, token_right) >= 90:
        return True

    return False