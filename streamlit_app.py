"""Web version of nordnetVisualizer.py, built with Streamlit + Plotly.

Run locally with:
    streamlit run streamlit_app.py

The numeric analysis mirrors deposit.py / yields.py (see plotlyCharts.py),
but rendering uses a single Plotly figure with animation frames instead of
matplotlib. Play/Pause and the slider are handled entirely client-side by
Plotly.js in the browser, so playback is smooth and doesn't require a
round-trip to the server for every transaction (unlike re-rendering a
matplotlib image per step).
"""
import streamlit as st

from cvsReader import read_csv_data
from plotlyCharts import build_figure

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

max_frames = st.slider(
    "Detail level (number of animation frames)",
    min_value=min(20, n), max_value=n, value=min(200, n),
    help="Higher = smoother/more granular animation but a larger page to load.",
)

# Rebuild the figure only when the dataset or detail level changes.
if st.session_state.get("fig_key") != (data_key, max_frames):
    with st.spinner("Building animation..."):
        st.session_state.fig = build_figure(data, max_frames=max_frames)
    st.session_state.fig_key = (data_key, max_frames)

st.plotly_chart(st.session_state.fig, use_container_width=True)
