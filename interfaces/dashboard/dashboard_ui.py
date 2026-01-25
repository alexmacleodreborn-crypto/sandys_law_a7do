import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_fragment,
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
    st.title("A7DO — Prebirth Structural Dashboard")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Growth Frame"):
        open_frame(state)

    if c2.button("➕ Add Growth Phase"):
        add_fragment(state)

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # OVERVIEW
    # ---------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": str(data["active_frame"]),
    "born": bool(data.get("birth") and data["birth"].get("born")),
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Structural Metrics")
    fig, ax = plt.subplots()
    ax.bar(metrics.keys(), metrics.values())
    st.pyplot(fig)

    # ---------------------------------
    # EMBODIMENT CANDIDATES
    # ---------------------------------
    st.subheader("Embodiment Candidates (Prebirth)")
    candidates = data.get("embodiment_candidates", [])

    if candidates:
        st.table(candidates)
    else:
        st.caption("No candidates yet — growth still stabilizing.")

    # ---------------------------------
    # WOMB
    # ---------------------------------
    st.subheader("Womb State")
    if data.get("womb"):
        st.json(data["womb"])
    else:
        st.caption("Womb inactive.")

    # ---------------------------------
    # BIRTH
    # ---------------------------------
    st.subheader("Birth Evaluation")
    if data.get("birth"):
        st.json(data["birth"])
    else:
        st.caption("Birth not yet eligible.")

    # ---------------------------------
    # MEMORY
    # ---------------------------------
    st.subheader("Structural Memory (Read-only)")
    memory = state.get("memory")
    if memory and memory.traces:
        st.table([
            {
                "tick": t.tick,
                "stability": round(t.stability, 3),
                "frame": t.frame_signature,
            }
            for t in memory.traces[-10:]
        ])

    # ---------------------------------
    # OBSERVER
    # ---------------------------------
    st.subheader("Observer Console")
    st.text_area(
        "Observer Output",
        render_chat_observer(snapshot),
        height=200,
    )