import streamlit as st
from sandys_law_a7do.bootstrap import tick_system


def render_dashboard(state, snapshot):
    st.title("A7DO — Prebirth Growth Monitor")

    if st.button("⏭ Tick"):
        tick_system(state)

    data = snapshot()

    st.metric("Tick", data["ticks"])

    st.subheader("Embodied Growth (Prebirth)")
    candidates = data.get("scuttling_candidates", [])

    if candidates:
        st.table(candidates)
    else:
        st.caption("Structural growth ongoing…")