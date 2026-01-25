# sandys_law_a7do/streamlit_app.py
# =====================================================
# STREAMLIT ENTRYPOINT (PATH-SAFE, FINAL)
# =====================================================

import sys
import pathlib
import streamlit as st

# -----------------------------------------------------
# FIX PYTHON PATH (REQUIRED FOR STREAMLIT)
# -----------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
PROJECT_ROOT = ROOT.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# -----------------------------------------------------
# NOW SAFE TO IMPORT PACKAGE
# -----------------------------------------------------
from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.dashboard_ui import render_dashboard

# -----------------------------------------------------
# STREAMLIT CONFIG
# -----------------------------------------------------
st.set_page_config(
    page_title="A7DO — Sandy’s Law",
    layout="wide",
)

# -----------------------------------------------------
# SESSION INITIALISATION (ONCE)
# -----------------------------------------------------
if "a7do_state" not in st.session_state:
    snapshot, state = build_system()
    st.session_state.a7do_state = state
    st.session_state.a7do_snapshot = snapshot

# -----------------------------------------------------
# RENDER DASHBOARD
# -----------------------------------------------------
render_dashboard(
    st.session_state.a7do_state,
    st.session_state.a7do_snapshot,
)

render_chat(
    st.session_state.a7do_snapshot
)