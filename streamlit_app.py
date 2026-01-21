# =====================================================
# STREAMLIT ENTRYPOINT (STABLE — DO NOT CHANGE)
# =====================================================

import sys
import pathlib
import streamlit as st

# -----------------------------------------------------
# PATH FIX (REQUIRED)
# -----------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

# -----------------------------------------------------
# IMPORTS
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
# SESSION INIT (ONCE)
# -----------------------------------------------------
if "initialized" not in st.session_state:
    snapshot, state = build_system()   # ✅ CORRECT
    st.session_state.state = state
    st.session_state.snapshot = snapshot
    st.session_state.initialized = True

# -----------------------------------------------------
# RENDER
# -----------------------------------------------------
render_dashboard(
    st.session_state.state,
    st.session_state.snapshot,
)