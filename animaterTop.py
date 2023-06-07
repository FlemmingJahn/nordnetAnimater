import random
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from deposit import *
from yields import *
date_text = "Dato"
posting_date_text = "Bogføringsdag"
filename = 'C:/tmp/inbetalinger.csv'

data = []
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

from itertools import count

def remap(fieldnames):
    price_count = count(1)
    return ['price{}'.format(next(price_count)) if f.startswith('price') else f
            for f in fieldnames]


import pandas as pd
def read_csv_file(filename):
    global data
    # read data from csv file
    with open(filename, 'r', encoding='utf-16') as csvfile:
        df = pd.read_csv(csvfile, delimiter='\t')
    data1 = df.to_dict('records')
    data = [row for row in reversed(data1)]

read_csv_file(filename)



fig1, axs = plt.subplots(nrows=3, ncols=3, figsize=(12, 6))
fig_ax = axs[0, 0]
fig_ax2 = axs[0, 1]
axs[0, 2].set_position([0, 0, 0, 0])

fig_ax3 = axs[1, 0]
fig_ax4 = axs[1, 1]
fig_yeild_years = axs[1, 2]

fig_yield_ax3 = axs[2, 0]
axs[2, 1].set_position([0, 0, 0, 0])
axs[2, 2].set_position([0, 0, 0, 0])

fig_yield_ax3.set_position([0.125, 0.1, 0.78, 0.2])

fig1.text(0.5, 0.04, 'x-axis', ha='center')
fig1.text(0.04, 0.5, 'y-axis', va='center', rotation='vertical')
title_text = fig1.suptitle('My Title', fontsize=20)
# Add blank subplots to ensure consistent dimensions
blank_axs = [axs[0, 2], axs[2, 1], axs[2, 2]]
for ax in blank_axs:
    ax.axis('off')

deposits_and_withdrawals = DepositsAndWithDrawals(fig1, fig_ax, fig_ax2, data=data)
deposits_and_withdrawals.analyze()
yields = Yields(fig1, fig_ax3, fig_ax4, fig_yeild_years, fig_yield_ax3 , data=data)

def update(frame):
    line, rects, text, labels = deposits_and_withdrawals.update(frame)
    total_line, yield_line, tax_line, valuta_rects, years_rects, stocks_rects, line_total_text, valuta_labels, years_labels, stocks_labels = yields.update(frame)
    return [line, *rects, text, *labels, total_line, yield_line, tax_line, *valuta_rects, *years_rects, *stocks_rects, line_total_text, *valuta_labels, *years_labels, *stocks_labels]

manager = plt.get_current_fig_manager()
manager.window.showMaximized()

ani = animation.FuncAnimation(fig1, update, frames=len(data), interval=1, repeat=False, blit=True)
plt.show()
