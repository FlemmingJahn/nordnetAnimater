import csv
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
import time
import tkinter as tk
from tkinter import filedialog


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

fig1, axs = plt.subplots(nrows=2, ncols=2, figsize=(12, 6))
fig_ax = axs[0,0]
fig_ax2 = axs[0,1]
fig_ax3 = axs[1,0]
fig_ax4 = axs[1,1]
fig1.text(0.5, 0.04, 'x-axis', ha='center')
fig1.text(0.04, 0.5, 'y-axis', va='center', rotation='vertical')
title_text = fig1.suptitle('My Title', fontsize=20)
class Yields():
    transaction_inserts = ['UDB.', 'MAK. UDB.']
    transaction_tax     = ['UDBYTTESKAT', 'KUPSKAT', 'MAK. UDBYTTESKAT']
    transaction_type = transaction_inserts + transaction_tax

    transaction_type_text = 'Transaktionstype'
    amount_text = 'Beløb'
    exchnage_text = 'Vekslingskurs'
    total_sums = [0]
    yield_sums = [0]
    tax_sums = [0]
    def __init__(self, _fig_yields, _ax, _ax_bars):
        self.fig_yields = _fig_yields
        self.ax = _ax
        self.ax_valuta_bars = _ax_bars
        self.line, = _ax.plot([], [], label='Total')
        self.line_yield, = _ax.plot([], [], label='Total')
        self.line_tax, = _ax.plot([], [], label='Total')

        self.text = _ax.text(0.02, 0.75, '', transform=_ax.transAxes)
        self.valutas_table = {}
        self.colors = self.get_random_colors(1)
        self.analyze()
        #self.init()
    def init(self):
        self.total_sums = [0]
        self.yield_sums = [0]
        self.tax_sums = [0]
        self.valutas_table = {}
        self.analyze()

    def analyze(self):
        for row in data:
            valuta = row['Valuta']
            if valuta not in self.valutas_table:
                self.valutas_table[valuta] = [0]

        valuta_keys = self.valutas_table.keys()
        self.colors = self.get_random_colors(len(valuta_keys))
        # calculate sums
        for row in data:
            valuta = row['Valuta']


            value = float(row['Beløb'].replace(".", "").replace(",", "."))
            exchange = float(row[self.exchnage_text].replace(".", "").replace(",", "."))
            value_in_dk = value*exchange


            if row['Transaktionstype'] in self.transaction_type:
                self.total_sums.append(self.total_sums[-1] + value_in_dk)
            else:
                self.total_sums.append(self.total_sums[-1])

            if row['Transaktionstype'] in self.transaction_inserts:
                self.yield_sums.append(self.yield_sums[-1] + value_in_dk)
                for k in valuta_keys:
                    if k == valuta:
                        self.valutas_table[k].append(self.valutas_table[k][-1] + value_in_dk)
                    else:
                        self.valutas_table[k].append(self.valutas_table[k][-1])
            else:
                for k in valuta_keys:
                    self.valutas_table[k].append(self.valutas_table[k][-1])
                self.yield_sums.append(self.yield_sums[-1])

            if row['Transaktionstype'] in self.transaction_tax:
                self.tax_sums.append(self.tax_sums[-1] - value_in_dk)
            else:
                self.tax_sums.append(self.tax_sums[-1])


        self.ax.set_title('Udbytter')
        self.ax.set_xlim(0, len(self.yield_sums))
        self.ax.set_ylim(0, max(self.yield_sums))

        self.ax_valuta_bars.set_title('Udbytter i valuta')


    def plot_line(self, i):
        self.line.set_data(range(i + 1), self.total_sums[:i + 1])
        self.line_yield.set_data(range(i + 1), self.yield_sums[:i + 1])
        self.line_tax.set_data(range(i + 1), self.tax_sums[:i + 1])

        self.ax.legend([f'Udbytte minus skat: {self.total_sums[i + 1]:,.0f} DKK', f'Udbytte: {self.yield_sums[i + 1]:,.0f} DKK', f'Skat: {self.tax_sums[i + 1]:,.0f} DKK'], loc='upper left')

    def get_random_colors(self, num_colors=4):
        """
        Returns a list of `num_colors` random colors.
        """
        colors = []
        for i in range(num_colors):
            hex_num = '#' + ''.join(random.choice('0123456789abcdef') for _ in range(6))
            colors.append(hex_num)
        return colors

    def plot_bars(self, index):
        for text_obj in self.ax_valuta_bars.texts:
            text_obj.remove()

        keys = self.valutas_table.keys()

        totals = []
        for v in self.valutas_table:
            totals.append(self.valutas_table[v][index])

        rects = self.ax_valuta_bars.bar(keys, totals, color=self.colors)

        for rect, total in zip(rects, totals):
            rect.set_height(total)

        for u, total in enumerate(totals):
            self.ax_valuta_bars.text(u, total, f'{total:,.0f} DKK', ha='center')


    def update(self, i):
        self.plot_line(i)
        self.plot_bars(i)
        return self.line, self.text

class DepositsAndWithDrawals():
    transaction_inserts = ['INDBETALING','INDSÆTTELSE', 'Straksoverførsel']
    transaction_type = ['INDBETALING', 'HÆVNING', "INDSÆTTELSE", 'Straksoverførsel']
    transaction_type_text = 'Transaktionstype'

    amount_text = 'Beløb'
    sum = [0]
    sums = [0]

    ax = None
    ax2 = None
    fid = None
    rects = None
    text = None

    def __init__(self, fig1, fig_ax, fig_ax2):
        self.ax = fig_ax
        self.ax2 = fig_ax2
        self.fig = fig1
        self.line, = fig_ax.plot([], [])

        self.text = fig_ax.text(0.02, 0.95, '', transform=fig_ax.transAxes)

        self.rects = 0

    def init(self):
        for rect in self.rects:
            rect.set_height(0)

        self.sum = [0]
        self.sums = [0]
        self.insert_sum = 0
        self.withdraw_sum = 0
        self.analyze()

    def analyze(self):
        # calculate sums
        for row in data:
            if row['Transaktionstype'] in self.transaction_type:
                self.sums.append(self.sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
            else:
                self.sums.append(self.sums[-1])
        self.ax2.set_title('Ind- og ud-betalinger')
        self.ax.set_title('', fontsize=40)
        self.ax.set_title('Ind- og ud-betalinger')
        # first plot: animation of sum of INDBETALING transactions
        self.ax.set_xlim(0, len(self.sums))
        self.ax.set_ylim(0, max(self.sums))

    def plot_line(self, i):
        self.line.set_data(range(i + 1), self.sums[:i + 1])
        self.ax.legend([f'Total: {self.sums[i]:,.0f} DKK'], loc='upper left')

    def plot_bars(self, index):
       for text_obj in self.ax2.texts:
            text_obj.remove()

       if data[index]['Transaktionstype'] in self.transaction_inserts:
           self.insert_sum += float(data[index]['Beløb'].replace(".", "").replace(",", "."))
       elif data[index]['Transaktionstype'] == 'HÆVNING':
           self.withdraw_sum += float(data[index]['Beløb'].replace(".", "").replace(",", "."))


       totals = [self.insert_sum, self.withdraw_sum]
       self.rects = self.ax2.bar(['INDBETALING', 'HÆVNING'], totals, color=['green', 'red'])

       for rect, total in zip(self.rects, totals):
           rect.set_height(total)

       for u, total in enumerate(totals):
           self.ax2.text(u, total, f'{total:,.0f} DKK', ha='center')

       return self.fig

    def get_fig(self):
        return self.fig

    insert_sum = 0
    withdraw_sum = 0


    def update(self, i):
        self.plot_line(i)
        self.plot_bars(i)
        return self.line, self.text

    def figure(self):
        pass

class Animate():
    deposits_and_withdrawals = DepositsAndWithDrawals(fig1, fig_ax, fig_ax2)
    yields = Yields(fig1, fig_ax3, fig_ax4)
    ani1 = None

    def update_data(self):
        is_first_frame = True  # flag to indicate the first frame

        def update(i):
            nonlocal is_first_frame
            if is_first_frame:
                is_first_frame = False
                return None  # skip the first frame

            title_text.set_text(f'{date_text}: {data[i][posting_date_text]}')

            self.deposits_and_withdrawals.update(i)
            self.yields.update(i)
        return update

    def plot(self):
        self.deposits_and_withdrawals.analyze()
        self.ani1 = animation.FuncAnimation(fig1,  self.update_data(), frames=len(data), interval= 1, repeat=False)

    def show(self):
        plt.show()

    def stop_animation(self):
        try:
            # Stop the current animation
            self.ani1.event_source.stop()
        except:
            pass
    def restart_animation(self):
        self.stop_animation()

        # Reset the plot data
        self.deposits_and_withdrawals.init()
        self.yields.init()

        # Create a new animation
        self.ani1 = animation.FuncAnimation(fig1, self.update_data(), frames=len(data), interval=1, blit=True, repeat=False)


    def restart_animation_event(self, event):
        self.restart_animation()

    def on_load_button_click(self, event):
        self.stop_animation()
        read_csv_file(filedialog.askopenfilename())
        self.restart_animation()
        plt.show()


animate = Animate()

# Create the restart button
button_ax = plt.axes([0.85, 0.01, 0.1, 0.05])
restart_button = Button(button_ax, 'Restart')

# Create the load button
load_button_ax = plt.axes([0.7, 0.01, 0.1, 0.05])
load_button = Button(load_button_ax, 'Load CVS file')
load_button.on_clicked(animate.on_load_button_click)

# Set the callback function for the restart button using the instance of the Animate class
restart_button.on_clicked(animate.restart_animation_event)

animate.plot()
animate.show()
