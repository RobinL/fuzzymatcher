from metaphone import doublemetaphone

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
    return new_tokens

def add_dmetaphones_to_col(x):
            tokens = x.split(" ")
            new_tokens = tokens_to_dmetaphones(tokens)
            tokens.extend(new_tokens)
            return " ".join(tokens)

def add_dmetaphone_to_concat_all(df):

        df["_concat_all"] =  df["_concat_all"].apply(add_dmetaphones_to_col)
