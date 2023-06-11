import pandas as pd
from cvsReader import *
from itertools import count
import csv

class CustomDictReader(csv.DictReader):
    def __init__(self, f, **kwargs):
        csv.DictReader.__init__(self, f, **kwargs)

    def __next__(self):
        row = csv.DictReader.__next__(self)
        new_row = {}
        for key, value in row.items():
            if key in new_row:
                new_key = f"{key}_2"
            else:
                new_key = key
            new_row[new_key] = value
        return new_row


def remap(fieldnames):
    price_count = count(1)
    return ['price{}'.format(next(price_count)) if f.startswith('price') else f
            for f in fieldnames]


def read_csv_file(filename):
    global data
    # read data from csv file
    with open(filename, 'r', encoding='utf-16') as csvfile:
        df = pd.read_csv(csvfile, delimiter='\t')
    data1 = df.to_dict('records')
    data = [row for row in reversed(data1)]
    return data


