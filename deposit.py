import csv
import random
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Button
from matplotlib.animation import FuncAnimation

from tkinter import filedialog

class DepositsAndWithDrawals:
    transaction_inserts = ['INDBETALING','INDSÆTTELSE', 'Straksoverførsel']
    transaction_type = ['INDBETALING', 'HÆVNING', "INDSÆTTELSE", 'Straksoverførsel']
    transaction_type_text = 'Transaktionstype'

    amount_text = 'Beløb'
    sum = [0]
    sums = [0]

    def __init__(self, fig1, fig_ax, fig_ax2, data):
        self.ax = fig_ax
        self.ax2 = fig_ax2
        self.fig = fig1
        self.line, = fig_ax.plot([], [])
        self.line_text = fig_ax.text(0.04, 0.90, '', transform=fig_ax.transAxes)
        self.bar_text =  fig_ax2.text(0.04, 0.90, '', transform=fig_ax.transAxes)
        self.insert_sum = [0]
        self.withdraw_sum = [0]
        self.rects = None
        self.data = data


    def init(self):
        self.sum = [0]
        self.sums = [0]
        self.insert_sum = [0]
        self.withdraw_sum = [0]
        self.analyze()
        return self.line, self.ax2, self.line_text

    def analyze(self):
        for row in self.data:
            if row['Transaktionstype'] in self.transaction_type:
                self.sums.append(self.sums[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
                if row['Transaktionstype'] in self.transaction_inserts:
                    self.insert_sum.append(self.insert_sum[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
                    self.withdraw_sum.append(self.withdraw_sum[-1])
                elif row['Transaktionstype'] == 'HÆVNING':
                    self.insert_sum.append(self.insert_sum[-1])
                    self.withdraw_sum.append(self.withdraw_sum[-1] + float(row['Beløb'].replace(".", "").replace(",", ".")))
            else:
                self.sums.append(self.sums[-1])
                self.insert_sum.append(self.insert_sum[-1])
                self.withdraw_sum.append(self.withdraw_sum[-1])

        self.ax2.set_title('Ind- og ud-betalinger')
        self.ax.set_title('', fontsize=40)
        self.ax.set_title('Ind- og ud-betalinger')
        self.ax.set_xlim(0, len(self.sums))
        self.ax.set_ylim(0, max(self.sums))

        self.ax2.set_ylim([min(self.withdraw_sum), max(self.insert_sum)])  # Adjust the range as needed

    def plot_line(self, i):
        if self.sums[:i + 1] == self.sums[:i]:
            return

        self.line_text.set_text(f'Total: {self.sums[i]:,.0f} DKK')
        self.line.set_data(range(i + 1), self.sums[:i + 1])

    def plot_bars(self, index):
        if self.insert_sum[index + 1] == self.insert_sum[index] and self.withdraw_sum[index + 1] == self.withdraw_sum[index]:
            return

        if self.rects is not None:
            for rect in self.rects:
                rect.remove()

        totals = [self.insert_sum[index + 1], self.withdraw_sum[index + 1]]
        self.rects = self.ax2.bar(['INDBETALING', 'HÆVNING'], totals, color=['green', 'red'])

        for u, total in enumerate(totals):
            self.ax2.text(u, total, f'{total:,.0f} DKK', ha='center')

        # Remove previous text objects
        for text in self.ax2.texts:
            text.set_visible(False)

        # Display the latest total values
        for rect, total in zip(self.rects, totals):
            height = rect.get_height()
            self.ax2.text(rect.get_x() + rect.get_width() / 2, height, f'{total:,.0f} DKK', ha='center', va='bottom')

        return self.rects

    def update(self, i):
        self.plot_line(i)
        self.plot_bars(i)
        return self.line, self.rects, self.line_text

    def figure(self):
        pass
