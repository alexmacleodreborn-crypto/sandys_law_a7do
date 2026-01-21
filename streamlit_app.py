# sandys_law_a7do/streamlit_app.py
# =====================================================
# STREAMLIT ENTRYPOINT (STABLE)
# =====================================================

import sys
import pathlib
import streamlit as st

# -----------------------------------------------------
# PATH FIX
# -----------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

# -----------------------------------------------------
# IMPORT CORE
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
# INITIALISE ONCE
# -----------------------------------------------------
if "a7do_initialized" not in st.session_state:
    _, snapshot, state = build_system()   # ✅ FIX HERE
    st.session_state.state = state
    st.session_state.snapshot = snapshot
    st.session_state.a7do_initialized = True

# -----------------------------------------------------
# RENDER
# -----------------------------------------------------
render_dashboard(
    st.session_state.state,
    st.session_state.snapshot,
)