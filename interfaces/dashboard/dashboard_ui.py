import streamlit as st
from sandys_law_a7do.bootstrap import tick_system


def render_dashboard(state, snapshot):
    st.title("A7DO — Prebirth Embodiment")

    if st.button("⏭ Tick"):
        tick_system(state)

    data = snapshot()
    metrics = data["metrics"]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tick", data["ticks"])
    c2.metric("Z", round(metrics["Z"], 3))
    c3.metric("Coherence", round(metrics["Coherence"], 3))
    c4.metric("Stability", round(metrics["Stability"], 3))

    st.subheader("Local Embodiment Candidates")

    candidates = data.get("embodiment_candidates", [])
    if candidates:
        st.table(candidates)
    else:
        st.caption("Embodiment forming…")