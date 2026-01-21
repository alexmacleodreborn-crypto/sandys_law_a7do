import sys
import pathlib
import streamlit as st

# --------------------------------------------------
# PATH FIX (STREAMLIT SAFE)
# --------------------------------------------------
ROOT = pathlib.Path(__file__).resolve().parent
PARENT = ROOT.parent
if str(PARENT) not in sys.path:
    sys.path.insert(0, str(PARENT))

from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.dashboard_ui import render_dashboard

# --------------------------------------------------
# STREAMLIT CONFIG (ONLY HERE)
# --------------------------------------------------
st.set_page_config(
    page_title="A7DO — Sandy’s Law",
    layout="wide",
)

# --------------------------------------------------
# SESSION INIT (ONCE)
# --------------------------------------------------
if "a7do_state" not in st.session_state:
    snapshot, state = build_system()
    st.session_state.a7do_state = state
    st.session_state.a7do_snapshot = snapshot

# --------------------------------------------------
# RENDER
# --------------------------------------------------
render_dashboard(
    st.session_state.a7do_state,
    st.session_state.a7do_snapshot,
)