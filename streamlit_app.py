"""Web version of nordnetVisualizer.py, built with Streamlit.

Run locally with:
    streamlit run streamlit_app.py

Reuses the existing analysis classes (DepositsAndWithDrawals, Yields) and CSV
parsing (cvsReader) so the numbers/plots stay identical to the desktop app;
only the animation driver changes from matplotlib's FuncAnimation to a
Streamlit slider + play button.
"""
import matplotlib.pyplot as plt
import streamlit as st

from cvsReader import read_csv_data
from deposit import DepositsAndWithDrawals
from yields import Yields

st.set_page_config(page_title="Nordnet Visualizer", layout="wide")
st.title("Nordnet Visualizer")
st.caption(
    "Upload your own Nordnet CSV export below. Nothing is stored on the "
    "server \u2014 your data is only processed in memory for this session."
)

uploaded = st.file_uploader(
    "Upload a Nordnet CSV export (UTF-16, tab separated)", type=["csv"]
)

if uploaded is None:
    st.info("Upload a CSV file to get started.")
    st.stop()

data = read_csv_data(uploaded)
data_key = f"upload:{uploaded.name}:{uploaded.size}"

if not data:
    st.warning("No transactions found in the selected file.")
    st.stop()

n = len(data)

# (Re)build the figure and analysis models only when the dataset changes,
# so the objects persist across reruns and behave like a real animation.
if st.session_state.get("data_key") != data_key:
    fig1, axs = plt.subplots(nrows=3, ncols=3, figsize=(14, 8), dpi=80)

    fig_ax, fig_ax2 = axs[0, 0], axs[0, 1]
    axs[0, 2].axis("off")

    fig_ax3, fig_ax4, fig_yield_years = axs[1, 0], axs[1, 1], axs[1, 2]
    fig_yield_ax3 = axs[2, 0]
    axs[2, 1].axis("off")
    axs[2, 2].axis("off")
    fig_yield_ax3.set_position([0.125, 0.1, 0.78, 0.2])

    deposits = DepositsAndWithDrawals(fig1, fig_ax, fig_ax2, data=data)
    yields_ = Yields(fig1, fig_ax3, fig_ax4, fig_yield_years, fig_yield_ax3, data=data)

    st.session_state.fig = fig1
    st.session_state.deposits = deposits
    st.session_state.yields = yields_
    st.session_state.data_key = data_key
    st.session_state.frame = n - 1
    st.session_state.playing = False

fig1 = st.session_state.fig
deposits = st.session_state.deposits
yields_ = st.session_state.yields

col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    label = "Pause" if st.session_state.playing else "Play"
    if st.button(label):
        st.session_state.playing = not st.session_state.playing
with col2:
    if st.button("Reset"):
        st.session_state.frame = 0
        st.session_state.playing = False
with col3:
    # Each Play step re-renders the whole figure and sends it over the
    # network, which is much slower than a local matplotlib animation.
    # Skipping several transactions per step keeps playback smooth even
    # on large files / slower hosting.
    steps_per_tick = st.slider(
        "Playback speed (transactions per step)", min_value=1, max_value=200, value=max(1, n // 200)
    )

st.session_state.frame = st.slider(
    "Transaction", min_value=0, max_value=n - 1, value=st.session_state.frame
)

deposits.update(st.session_state.frame)
yields_.update(st.session_state.frame)

st.pyplot(fig1)

if st.session_state.playing:
    if st.session_state.frame >= n - 1:
        st.session_state.playing = False
    else:
        st.session_state.frame = min(st.session_state.frame + steps_per_tick, n - 1)
        st.rerun()
