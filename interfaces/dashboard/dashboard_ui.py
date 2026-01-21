# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py

import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_fragment,
    close_frame,
)
from sandys_law_a7do.engine.tick_engine import step_tick


def render_dashboard(state, snapshot):
    # ---------------------------------
    # INITIAL SNAPSHOT
    # ---------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # INIT HISTORY + EVENT FLAG (ONCE)
    # ---------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }

    if "record_history" not in state:
        state["record_history"] = False

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Sandy’s Law System Dashboard")

    # ---------------------------------
    # CONTROLS (STATE MUTATION ONLY HERE)
    # ---------------------------------
    st.subheader("Controls")
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Fragment"):
        add_fragment(state)

    if c3.button("⏹ Close Frame"):
        close_frame(state)
        state["record_history"] = True   # ✅ episode boundary

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)       # ✅ ONLY place tick is called
        state["record_history"] = True   # ✅ real system event

    # ---------------------------------
    # SNAPSHOT AFTER CONTROLS
    # ---------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------
    st.subheader("System Overview")
    st.json(
        {
            "ticks": data["ticks"],
            "active_frame": (
                f"{data['active_frame'].domain}:{data['active_frame'].label}"
                if data["active_frame"]
                else "none"
            ),
            "memory_count": data["memory_count"],
        }
    )

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Metrics")
    m1, m2, m3 = st.columns(3)
    m1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))

    # ---------------------------------
    # RECORD HISTORY (EVENT-BASED ONLY)
    # ---------------------------------
    if state["record_history"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["record_history"] = False

    # ---------------------------------
    # METRIC EVOLUTION PLOT
    # ---------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        state["history"]["ticks"],
        state["history"]["Z"],
        label="Z (Fragmentation)",
        color="red",
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Coherence"],
        label="Coherence",
        color="blue",
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Stability"],
        label="Stability",
        )
       