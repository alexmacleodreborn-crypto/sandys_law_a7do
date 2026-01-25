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

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Prebirth / Birth System Monitor")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    st.subheader("Controls")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Phase"):
        add_fragment(state, kind="growth_phase")

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # SYSTEM STATE
    # ---------------------------------
    st.subheader("System State")
    st.json({
        "ticks": data["ticks"],
        "frame": str(data["active_frame"]) if data["active_frame"] else "none",
        "born": data.get("birth", {}).get("born", False),
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Structural Metrics")
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Fragmentation (Z)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # ---------------------------------
    # WOMB
    # ---------------------------------
    st.subheader("Womb Environment")
    if data["womb"]:
        st.json(data["womb"])
    else:
        st.caption("Womb inactive.")

    # ---------------------------------
    # LOCAL EMBODIMENT (IMPORTANT)
    # ---------------------------------
    st.subheader("Local Embodiment Formation (Prebirth)")

    local = data.get("local_embodiment")
    if local:
        st.table(local)
    else:
        st.caption("No local embodiment patterns yet.")

    # ---------------------------------
    # BIRTH
    # ---------------------------------
    st.subheader("Birth Evaluation")
    if data["birth"]:
        st.json(data["birth"])
    else:
        st.caption("Birth not evaluated yet.")

    # ---------------------------------
    # FINAL SNAPSHOT
    # ---------------------------------
    st.subheader("Full Snapshot")
    st.json(data)