# sandys_law_a7do/streamlit_app.py
"""
A7DO — Sandy’s Law
SINGLE Streamlit entry point
"""

import streamlit as st

from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.dashboard_ui import render_dashboard


# --------------------------------------------------
# INIT SYSTEM ONCE
# --------------------------------------------------

if "a7do_state" not in st.session_state:
    _, snapshot, state = build_system()
    st.session_state.a7do_state = state
    st.session_state.snapshot_fn = snapshot

state = st.session_state.a7do_state
snapshot = st.session_state.snapshot_fn


# --------------------------------------------------
# STREAMLIT SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="A7DO — Sandy’s Law",
    layout="wide",
)

st.title("A7DO — Sandy’s Law System Dashboard")


# --------------------------------------------------
# RENDER UI
# --------------------------------------------------

render_dashboard(state, snapshot)