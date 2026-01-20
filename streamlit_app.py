# sandys_law_a7do/streamlit_app.py
"""
A7DO — Sandy’s Law
Single Streamlit entry point (Streamlit-safe)
"""

import sys
from pathlib import Path

# --------------------------------------------------
# MAKE PACKAGE IMPORTABLE (CRITICAL FOR STREAMLIT)
# --------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --------------------------------------------------
# NOW SAFE TO IMPORT PACKAGE
# --------------------------------------------------

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