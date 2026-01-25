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
    data = snapshot()
    metrics = data["metrics"]

    if "history" not in state:
        state["history"] = {"ticks": [], "Z": [], "Coherence": [], "Stability": []}

    st.title("A7DO — Sandy’s Law Development Dashboard")

    # ================= CONTROLS =================
    st.subheader("Development Controls")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Development Frame"):
        open_frame(state)
    if c2.button("🌱 Add Growth Event"):
        add_growth_event(state, phase=data["phase"])
    if c3.button("⏹ Close Frame"):
        close_frame(state)
    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ================= OVERVIEW =================
    st.subheader("System Overview")
    st.json({
        "tick": data["ticks"],
        "phase": data["phase"],
        "born": data.get("birth", {}).get("born", False),
        "memory_traces": data["memory_count"],
    })

    # ================= METRICS =================
    st.subheader("Structural Metrics")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Fragmentation (Z)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # ================= HISTORY =================
    state["history"]["ticks"].append(data["ticks"])
    state["history"]["Z"].append(metrics["Z"])
    state["history"]["Coherence"].append(metrics["Coherence"])
    state["history"]["Stability"].append(metrics["Stability"])

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # ================= WOMB =================
    st.subheader("Prebirth — Womb State")
    if data["womb"]:
        st.table([{"metric": k, "value": v} for k, v in data["womb"].items()])
    else:
        st.caption("Womb inactive")

    # ================= EMBODIMENT =================
    st.subheader("Embodiment Ledger (Read-Only)")
    if data["embodiment"]:
        st.table([{"metric": k, "value": v} for k, v in data["embodiment"].items()])
    else:
        st.caption("No invariants yet")

    # ================= BIRTH =================
    st.subheader("Birth Evaluation")
    st.json(data.get("birth"))

    # ================= CHAT =================
    st.subheader("Observer Console")
    st.text_area(
        "Observer Output",
        render_chat_observer(snapshot),
        height=220,
    )

    st.subheader("Final Snapshot")
    st.json(data)