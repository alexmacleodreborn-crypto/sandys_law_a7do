import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    close_frame,
    add_growth_event,
)
from sandys_law_a7do.engine.tick_engine import step_tick
from sandys_law_a7do.interfaces.chat.observer import render_chat_observer


def render_dashboard(state, snapshot):
    # ---------------------------------
    # SNAPSHOT
    # ---------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # INIT HISTORY
    # ---------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Sandy’s Law Development Dashboard")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    st.subheader("Controls")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Development Frame"):
        open_frame(state)

    if c2.button("🌱 Add Growth Event"):
        add_growth_event(state, phase=data.get("phase", "prebirth"))

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------
    birth = data.get("birth")
    born = birth["born"] if isinstance(birth, dict) else False

    st.subheader("System Overview")
    st.json({
        "tick": data["ticks"],
        "phase": data.get("phase"),
        "born": born,
        "memory_traces": data["memory_count"],
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Structural Metrics")
    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # ---------------------------------
    # RECORD HISTORY
    # ---------------------------------
    state["history"]["ticks"].append(data["ticks"])
    state["history"]["Z"].append(metrics["Z"])
    state["history"]["Coherence"].append(metrics["Coherence"])
    state["history"]["Stability"].append(metrics["Stability"])

    # ---------------------------------
    # METRIC EVOLUTION
    # ---------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")
    ax.set_ylim(0.0, 1.05)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # EMBODIMENT (READ-ONLY)
    # ---------------------------------
    st.subheader("Embodiment Ledger Summary")
    embodiment = data.get("embodiment")

    if isinstance(embodiment, dict):
        st.table([{"metric": k, "value": v} for k, v in embodiment.items()])
    else:
        st.caption("No embodied invariants yet.")

    # ---------------------------------
    # PREBIRTH / WOMB
    # ---------------------------------
    st.subheader("Prebirth — Womb State")
    womb = data.get("womb")

    if isinstance(womb, dict):
        st.table([{"metric": k, "value": v} for k, v in womb.items()])
    else:
        st.caption("Womb inactive or birth completed.")

    # ---------------------------------
    # BIRTH STATE
    # ---------------------------------
    st.subheader("Birth Evaluation")

    if isinstance(birth, dict):
        st.json(birth)
    else:
        st.caption("Birth not yet evaluated.")

    # ---------------------------------
    # CHAT OBSERVER
    # ---------------------------------
    st.subheader("Observer Console")
    st.text_area(
        "Observer Output",
        render_chat_observer(snapshot),
        height=220,
    )

    # ---------------------------------
    # FINAL STATE
    # ---------------------------------
    st.subheader("Final Snapshot")
    st.json(data)