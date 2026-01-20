# sandys_law_a7do/streamlit_app.py
# =====================================================
# STREAMLIT ENTRYPOINT (PATH-SAFE)
# =====================================================

import sys
import pathlib
import streamlit as st

# -----------------------------------------------------
# FIX PYTHON PATH (CRITICAL FOR RELATIVE IMPORTS)
# -----------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

# -----------------------------------------------------
# NOW SAFE TO IMPORT PACKAGE MODULES
# -----------------------------------------------------
from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.dashboard_ui import render_dashboard

# -----------------------------------------------------
# STREAMLIT CONFIG (ONLY HERE)
# -----------------------------------------------------
st.set_page_config(
    page_title="A7DO — Sandy’s Law",
    layout="wide",
)

# -----------------------------------------------------
# SESSION INITIALISATION (ONCE)
# -----------------------------------------------------
if "initialized" not in st.session_state:
    _, snapshot, state = build_system()
    st.session_state.state = state
    st.session_state.snapshot = snapshot
    st.session_state.initialized = True

# -----------------------------------------------------
# RENDER DASHBOARD
# -----------------------------------------------------
render_dashboard(
    st.session_state.state,
    st.session_state.snapshot,
)