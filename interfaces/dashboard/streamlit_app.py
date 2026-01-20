# interfaces/dashboard/streamlit_app.py

import streamlit as st

from interfaces.dashboard.frame_inspector import render_frame_inspector
from tools.visualization import bar_view


def main(system_snapshot_provider):
    st.set_page_config(page_title="A7DO Dashboard", layout="wide")
    st.title("A7DO — Sandy’s Law System Dashboard")

    snapshot = system_snapshot_provider()

    st.subheader("System Overview")
    st.code(snapshot, language="json")

    if "metrics" in snapshot:
        st.subheader("Metrics")
        st.text(bar_view(snapshot["metrics"]))

    if "frames" in snapshot:
        render_frame_inspector(snapshot["frames"])


if __name__ == "__main__":
    st.error("Dashboard must be launched by system bootstrap")
