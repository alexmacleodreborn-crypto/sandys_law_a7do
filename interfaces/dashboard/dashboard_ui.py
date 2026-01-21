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
    # INIT HISTORY (ONCE)
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

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)   # ✅ ONLY place tick is called

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
    # RECORD HISTORY (PURE APPEND)
    # ---------------------------------
    state["history"]["ticks"].append(data["ticks"])
    state["history"]["Z"].append(metrics["Z"])
    state["history"]["Coherence"].append(metrics["Coherence"])
    state["history"]["Stability"].append(metrics["Stability"])

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
        color="green",
    )

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # MEMORY TIMELINE (READ-ONLY)
    # ---------------------------------
    st.subheader("Memory Timeline (Recent)")

    memory = state.get("memory")

    if memory and hasattr(memory, "traces") and memory.traces:
        recent = memory.traces[-10:]  # last 10 traces only

        st.table([
            {
                "tick": t.tick,
                "Z": round(t.features.get("Z", 0.0), 3),
                "coherence": round(t.features.get("coherence", 0.0), 3),
                "stability": round(t.features.get("stability", 0.0), 3),
                "frame": t.features.get("frame_signature", "none"),
                "tags": ", ".join(t.tags),
            }
            for t in recent
        ])
    else:
        st.caption("No memory traces recorded yet.")

    # ---------------------------------
    # FINAL STATE
    # ---------------------------------
    st.subheader("Final State")
    st.json(data)