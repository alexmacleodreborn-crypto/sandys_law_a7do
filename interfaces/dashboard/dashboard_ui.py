import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_fragment,
    close_frame,
)
from sandys_law_a7do.engine.tick_engine import step_tick


def render_dashboard(state, snapshot):
    data = snapshot()
    metrics = data["metrics"]

    st.title("A7DO — Prebirth System")

    # --------------------------------------------------
    # Controls
    # --------------------------------------------------
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Phase"):
        add_fragment(state, kind="growth_phase")

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # --------------------------------------------------
    # Overview
    # --------------------------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": (
            f"{data['active_frame'].domain}:{data['active_frame'].label}"
            if data["active_frame"] else "none"
        ),
        "born": data["birth"]["born"] if data["birth"] else False,
    })

    # --------------------------------------------------
    # Metrics
    # --------------------------------------------------
    st.subheader("Structural Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Z", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # --------------------------------------------------
    # Womb
    # --------------------------------------------------
    st.subheader("Womb State")
    if data["womb"]:
        st.json(data["womb"])
    else:
        st.caption("Womb inactive")

    # --------------------------------------------------
    # Scuttling
    # --------------------------------------------------
    st.subheader("Scuttling — Embodied Growth")

    sc = data["scuttling"]

    st.markdown("### Regions")
    st.json(sc["regions"])

    st.markdown("### Local Embodiment Candidates")
    if sc["candidates"]:
        st.table(sc["candidates"])
    else:
        st.caption("No candidates yet (early prebirth)")

    # --------------------------------------------------
    # Birth
    # --------------------------------------------------
    st.subheader("Birth Evaluation")
    if data["birth"]:
        st.json(data["birth"])
    else:
        st.caption("Birth not yet evaluated")

    # --------------------------------------------------
    # Final Snapshot
    # --------------------------------------------------
    st.subheader("Raw Snapshot")
    st.json(data)