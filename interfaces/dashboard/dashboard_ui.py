import streamlit as st
from sandys_law_a7do.engine.tick_engine import step_tick


def render_dashboard(state, snapshot):
    st.title("A7DO — Development Dashboard")

    # -----------------------------
    # Controls
    # -----------------------------
    if st.button("⏭ Tick"):
        step_tick(state)

    data = snapshot()

    # -----------------------------
    # Womb
    # -----------------------------
    st.subheader("Prebirth — Womb")
    if data["womb"]:
        st.json(data["womb"])
    else:
        st.caption("Womb not yet active")

    # -----------------------------
    # Scuttling / Candidates
    # -----------------------------
    st.subheader("Embodied Growth (Candidates)")
    if data["candidates"]:
        st.table(data["candidates"])
    else:
        st.caption("No candidates yet")

    # -----------------------------
    # Birth
    # -----------------------------
    st.subheader("Birth State")
    if data["birth"]:
        st.json(data["birth"])
    else:
        st.caption("Birth not yet triggered")