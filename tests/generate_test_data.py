import pandas as pd
import numpy as np 
import random
import datetime
from faker import Faker

def get_random_by_freq(csv_path, field, num_elements):
    df = pd.read_csv(csv_path)
    elements = df[field]
    probabilites = df["freq"]/sum(df["freq"])
    return np.random.choice(elements, num_elements, p= list(probabilites))

def get_fakes(fake_fn, num_elements):
    result = []
    for i in range(num_elements):
        result.append(fake_fn())
    return result

def switch(my_string):
    pos1 = random.randrange(0,len(my_string)) 
    pos2 = random.randrange(0,len(my_string)) 
    my_string = list(my_string)
    char1 = my_string[pos1]
    char2 = my_string[pos2]
    my_string[pos1] = char2
    my_string[pos2] = char1
    return "".join(my_string)

def new_letter(my_string):
    pos1 = random.randrange(0,len(my_string)) 
    letter = random.choice(string.ascii_lowercase)
    return my_string[:pos1] + letter + my_string[pos1:]

def delete_letter(my_string):
    pos1 = random.randrange(1,len(my_string)) 
    return my_string[:pos1] + my_string[pos1+1:]

def corrupt_string(my_string, num_switches=1,num_new_letters=0,num_deletes=1):
    
    for i in range(num_switches):
        my_string = switch(my_string)
        
    for i in range(num_new_letters):
        my_string = new_letter(my_string)
        
    for i in range(num_deletes):
        my_string = delete_letter(my_string)
        
    return my_string

def corrupt_dob(dob):
    fmt = "%Y-%m-%d"
    date_1 = datetime.datetime.strptime(dob, fmt)
    end_date = date_1 + datetime.timedelta(days=random.randint(-100,100))
    return end_date.strftime(fmt)

def create_test_data(num_elements = 100):
    fake = Faker()

    first_names = pd.read_csv("data/_first_names.csv")
    surnames = pd.read_csv("data/_surnames.csv")

    data = {}
    data["01first_name"] = get_random_by_freq("data/_first_names.csv", "name", num_elements)
    data["02surname"] = get_random_by_freq("data/_surnames.csv", "surname", num_elements)
    data["03dob"] = get_fakes(fake.date, num_elements)
    data["04city"] = get_random_by_freq("data/_cities.csv", "city", num_elements)
    data["05email"] = get_fakes(fake.company_email, num_elements)

    df_left = pd.DataFrame(data)
    df_left.columns = [c[2:] for c in df_left.columns]

    df_right = df_left.copy()

    for df in [df_left, df_right]:
        for r in df.iterrows():
            index = r[0]
            row = r[1]

            for col in ["first_name", "surname", "city", "email"]:
                if (random.random()>0.8):
                    df.loc[index, col] = corrupt_string(row[col])

            # Sometimes switch first name and surname
            if (random.random()>0.9):
                surname = row["surname"]
                first_name = row["first_name"]
                df.loc[index, "first_name"] = surname
                df.loc[index, "surname"] = first_name

            # Corrupt the dob
            if random.random() > 0.8:
                df.loc[index, "dob"] = corrupt_dob(row["dob"])
    return df_left, df_right