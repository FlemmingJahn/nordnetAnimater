import matplotlib
from deposit import *
from yields import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from readData import *
import argparse

parser = argparse.ArgumentParser(description='Process a filename.')
parser.add_argument('-f', '--filename', default=None, help='Fil der indeholder Nordnet CVS data')
parser.add_argument('-w', '--wxagg', dest='wxagg', action='store_true', help='Brug XXAgg libary')
args = parser.parse_args()
filename = args.filename
use_wxagg = args.wxagg

if use_wxagg:
    matplotlib.use('WXAgg')

data = get_data(filename)

date_text = "Dato"
posting_date_text = "Bogføringsdag"

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

def maximize_window():
    f = fig1
    x = 0
    y = 0
    h = 4096
    w = 2160
    """Move figure's upper left corner to pixel (x, y)"""
    backend = matplotlib.get_backend()
    if backend == 'TkAgg':
        pass
        #f.canvas.manager.window.wm_geometry("+%d+%d+%d+%d" % (x, y, w, h))
    elif backend == 'WXAgg':
        fig1.canvas.manager.window.Maximize()

        #f.canvas.manager.window.SetPosition((x, y, w, h))
    else:
        # This works for QT and GTK
        # You can also use window.setGeometry
        f.canvas.manager.window.move(x, y, w, h)
    pass


def start_animation():
    global ani
    ani = animation.FuncAnimation(fig1, update, frames=len(data), interval=1, repeat=False, blit=True)
    plt.show()

maximize_window()
start_animation()
