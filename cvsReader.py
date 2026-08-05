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
    # read data from csv file on disk
    with open(filename, 'r', encoding='utf-16') as csvfile:
        return read_csv_data(csvfile)


def read_csv_data(file_obj):
    """Parse Nordnet CSV data from an already-open text stream or a
    binary/bytes-like file object (e.g. Streamlit's uploaded file),
    returning the rows in chronological order.
    """
    import io

    if hasattr(file_obj, 'read'):
        # Detect binary mode (e.g. Streamlit UploadedFile) and wrap it
        # so pandas can decode the utf-16 text.
        sample = file_obj.read(0)
        if isinstance(sample, bytes):
            file_obj = io.TextIOWrapper(file_obj, encoding='utf-16')

    df = pd.read_csv(file_obj, delimiter='\t')
    data1 = df.to_dict('records')
    return [row for row in reversed(data1)]


