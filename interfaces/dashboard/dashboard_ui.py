import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_phase_signal,
    close_frame,
)
from sandys_law_a7do.engine.tick_engine import step_tick
from sandys_law_a7do.interfaces.chat.observer import render_chat_observer


def render_dashboard(state, snapshot):
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Sandy’s Law System Dashboard")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    st.subheader("Controls")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Phase (Prebirth)"):
        add_phase_signal(
            state,
            phase="prebirth",
            payload={"growth_step": state["ticks"]},
        )

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": str(data["active_frame"]),
        "memory_count": data["memory_count"],
        "born": data.get("birth", {}).get("born") if data.get("birth") else False,
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Structural Metrics")
    cols = st.columns(4)
    cols[0].metric("Z", round(metrics["Z"], 3))
    cols[1].metric("Coherence", round(metrics["Coherence"], 3))
    cols[2].metric("Stability", round(metrics["Stability"], 3))
    cols[3].metric("Load", round(metrics["Load"], 3))

    # ---------------------------------
    # EMBODIMENT
    # ---------------------------------
    st.subheader("Embodiment Ledger (Read-Only)")
    st.json(data["embodiment"])

    # ---------------------------------
    # WOMB
    # ---------------------------------
    st.subheader("Prebirth — Womb State")
    st.json(data["womb"] or {"status": "inactive"})

    # ---------------------------------
    # BIRTH
    # ---------------------------------
    st.subheader("Birth Evaluation")
    st.json(data["birth"] or {"status": "not yet eligible"})

    # ---------------------------------
    # CHAT OBSERVER
    # ---------------------------------
    st.subheader("Observer Console")
    st.text_area(
        "A7DO Observer Output",
        render_chat_observer(snapshot),
        height=220,
    )

    # ---------------------------------
    # FINAL SNAPSHOT
    # ---------------------------------
    st.subheader("Final Snapshot")
    st.json(data)