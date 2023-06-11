from deposit import *
from yields import *
from cvsReader import *
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button
import matplotlib.animation as animation
from matplotlib.widgets import Button
from tkinter import Tk, filedialog
def set_filename():
    global filename
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename()
    if file_path:
        filename = file_path
        # Update data and perform analysis with the new filename
        global data
        data = read_csv_file(filename)

date_text = "Dato"
posting_date_text = "Bogføringsdag"
filename = 'C:/tmp/inbetalinger.csv'
set_filename()

data = read_csv_file(filename)
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
# Add blank subplots to ensure consistent dimensions
blank_axs = [axs[0, 2], axs[2, 1], axs[2, 2]]
for ax in blank_axs:
    ax.axis('off')

deposits_and_withdrawals = DepositsAndWithDrawals(fig1, fig_ax, fig_ax2, data=data)
yields = Yields(fig1, fig_ax3, fig_ax4, fig_yeild_years, fig_yield_ax3, data=data)

def update(frame):
    line, rects, text, labels = deposits_and_withdrawals.update(frame)
    total_line, yield_line, tax_line, valuta_rects, years_rects, stocks_rects, line_total_text, line_tax_text, line_yeilds_after_tax_text, valuta_labels, years_labels, stocks_labels = yields.update(frame)
    return [line, *rects, text, *labels, total_line, yield_line, tax_line, *valuta_rects, *years_rects, *stocks_rects, line_total_text, line_tax_text, line_yeilds_after_tax_text, *valuta_labels, *years_labels, *stocks_labels]

manager = plt.get_current_fig_manager()
manager.window.showMaximized()

def start_animation():
    global ani
    ani = animation.FuncAnimation(fig1, update, frames=len(data), interval=1, repeat=False, blit=True)
    plt.show()

start_animation()