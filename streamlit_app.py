import streamlit as st
from .bootstrap import build_system
from .interfaces.dashboard.dashboard_ui import render_dashboard

st.set_page_config(layout="wide")

if "a7do_state" not in st.session_state:
    snapshot, state = build_system()
    st.session_state.a7do_state = state
    st.session_state.a7do_snapshot = snapshot

render_dashboard(
    st.session_state.a7do_state,
    st.session_state.a7do_snapshot,
)