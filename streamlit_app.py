import streamlit as st

from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.dashboard_ui import render_dashboard

# --------------------------------------------------
# STREAMLIT CONFIG — MUST BE HERE AND ONLY HERE
# --------------------------------------------------
st.set_page_config(
    page_title="A7DO — Sandy’s Law",
    layout="wide",
)

# --------------------------------------------------
# SESSION INITIALISATION (ONCE)
# --------------------------------------------------
if "initialized" not in st.session_state:
    _, snapshot, state = build_system()
    st.session_state.state = state
    st.session_state.snapshot = snapshot
    st.session_state.initialized = True

# --------------------------------------------------
# RENDER UI
# --------------------------------------------------
render_dashboard(
    st.session_state.state,
    st.session_state.snapshot,
)