import itertools

import matplotlib
from deposit import *
from yields import *
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.widgets import Slider
from readData import *
import argparse
#import wx
import tkinter as tk
import matplotlib.backends.backend_tkagg as tkagg


parser = argparse.ArgumentParser(description='Process a filename.')
parser.add_argument('-f', '--filename', default=None, help='Fil der indeholder Nordnet CVS data')
parser.add_argument('-w', '--wxagg', dest='wxagg', action='store_true', help='Brug XXAgg libary')
parser.add_argument('-s', '--save', dest='save', action='store_true', help='Save the animation as an MP4 file')
parser.add_argument('-i', '--interval', type=int, default=1, help='Millisekunder mellem hvert billede ved start (kan justeres live med slideren). Default: 1')
parser.add_argument('--step', type=int, default=1, help='Antal transaktioner der springes frem per billede ved start (kan justeres live med slideren). Default: 1')
args = parser.parse_args()
filename = args.filename
use_wxagg = args.wxagg
save_animation = args.save
interval = args.interval
step = max(1, args.step)

if use_wxagg:
    matplotlib.use('WXAgg')

data = get_data(filename)

date_text = "Dato"
posting_date_text = "Bogføringsdag"

fig1, axs = plt.subplots(nrows=3, ncols=3, figsize=(12, 6))
plt.subplots_adjust(bottom=0.2)
fig_ax = axs[0, 0]
fig_ax2 = axs[0, 1]
axs[0, 2].set_position([0, 0, 0, 0])

fig_ax3 = axs[1, 0]
fig_ax4 = axs[1, 1]
fig_yeild_years = axs[1, 2]

fig_yield_ax3 = axs[2, 0]
axs[2, 1].set_position([0, 0, 0, 0])
axs[2, 2].set_position([0, 0, 0, 0])

fig_yield_ax3.set_position([0.125, 0.22, 0.78, 0.15])

fig1.text(0.5, 0.04, 'x-axis', ha='center')
fig1.text(0.04, 0.5, 'y-axis', va='center', rotation='vertical')
# Add blank subplots to ensure consistent dimensions
blank_axs = [axs[0, 2], axs[2, 1], axs[2, 2]]
for ax in blank_axs:
    ax.axis('off')

deposits_and_withdrawals = DepositsAndWithDrawals(fig1, fig_ax, fig_ax2, data=data)
yields = Yields(fig1, fig_ax3, fig_ax4, fig_yeild_years, fig_yield_ax3, data=data)

# Live-adjustable playback speed. `position` tracks how far through the
# data we currently are; `playback` holds the current step size (how many
# transactions to advance per frame) and interval (ms between frames),
# both changeable at runtime via the sliders below without restarting.
position = {"i": 0}
playback = {"step": step, "interval": interval}

step_ax = fig1.add_axes([0.15, 0.08, 0.3, 0.03])
step_slider = Slider(step_ax, 'Trin/billede', 1, max(50, step), valinit=step, valstep=1)

interval_ax = fig1.add_axes([0.55, 0.08, 0.3, 0.03])
interval_slider = Slider(interval_ax, 'Ventetid (ms)', 1, max(200, interval), valinit=interval, valstep=1)


def on_step_change(val):
    playback["step"] = max(1, int(val))


def on_interval_change(val):
    playback["interval"] = max(1, int(val))
    if 'ani' in globals():
        ani.event_source.interval = playback["interval"]


step_slider.on_changed(on_step_change)
interval_slider.on_changed(on_interval_change)


def update(_):
    idx = min(position["i"], len(data) - 1)
    line, rects, text, labels = deposits_and_withdrawals.update(idx)
    total_line, yield_line, tax_line, valuta_rects, years_rects, stocks_rects, line_total_text, line_tax_text, line_yeilds_after_tax_text, valuta_labels, years_labels, stocks_labels = yields.update(idx)

    if idx >= len(data) - 1:
        ani.event_source.stop()
    else:
        position["i"] = min(position["i"] + playback["step"], len(data) - 1)

    return [line, *rects, text, *labels, total_line, yield_line, tax_line, *valuta_rects, *years_rects, *stocks_rects, line_total_text, line_tax_text, line_yeilds_after_tax_text, *valuta_labels, *years_labels, *stocks_labels]


def start_animation():
    global ani

    ani = animation.FuncAnimation(fig1, update, frames=itertools.count(), interval=playback["interval"], repeat=False, blit=True, cache_frame_data=False)

    if save_animation:
        Writer = animation.writers['ffmpeg']
        writer = Writer(fps=15, metadata=dict(artist='Me'), bitrate=1800)
        line_ani.save('lines.mp4', writer=writer)
     

    else:
        plt.show()


start_animation()


exit(0)

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

maximize_window()


