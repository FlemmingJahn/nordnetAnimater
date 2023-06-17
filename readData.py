from tkinter import Tk, filedialog
from cvsReader import *

def get_data(filename = None):
    if filename is None:
        root = Tk()
        root.withdraw()
        file_path = filedialog.askopenfilename()
        if file_path:
            filename = file_path

    return read_csv_file(filename)