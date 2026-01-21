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
    # INIT HISTORY + FLAGS (ONCE)
    # ---------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
            "Load": [],
            "Attention": [],
            "PredErr": [],
        }

    if "record_history" not in state:
        state["record_history"] = False

    if "last_recorded_tick" not in state:
        state["last_recorded_tick"] = None

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
        state["record_history"] = True

    if c2.button("➕ Add Fragment"):
        add_fragment(state)
        state["record_history"] = True

    if c3.button("⏹ Close Frame"):
        close_frame(state)
        state["record_history"] = True   # episode boundary

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)       # ONLY place tick is called
        state["record_history"] = True

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
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("PredErr", round(metrics.get("PredErr", 0.0), 3))
    m5.metric("Attention", round(metrics.get("AttentionLast", 1.0), 3))

    # ---------------------------------
    # RECORD HISTORY (FRAME-AWARE + SAFE)
    # ---------------------------------
    should_record = (data["active_frame"] is not None) or state["record_history"]

    if should_record and state["last_recorded_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["history"]["Load"].append(metrics.get("Load", 0.0))
        state["history"]["Attention"].append(metrics.get("AttentionLast", 1.0))
        state["history"]["PredErr"].append(metrics.get("PredErr", 0.0))

        state["last_recorded_tick"] = data["ticks"]
        state["record_history"] = False

    # ---------------------------------
    # METRIC EVOLUTION PLOT
    # ---------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")
    ax.plot(state["history"]["ticks"], state["history"]["Load"], label="Load", linestyle=":")
    ax.plot(state["history"]["ticks"], state["history"]["Attention"], label="Attention", linestyle="--")
    ax.plot(state["history"]["ticks"], state["history"]["PredErr"], label="PredErr", linestyle="--")

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.set_ylim(0.0, 1.55)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # PREFERENCE (READ-ONLY)
    # ---------------------------------
    st.subheader("Preference (Read-only Bias)")
    st.json(
        {
            "top": data.get("preference_top", []),
            "last_update": data.get("last_preference_update"),
        }
    )

    # ---------------------------------
    # MEMORY TIMELINE (READ-ONLY)
    # ---------------------------------
    st.subheader("Memory Timeline (Recent)")

    memory = state.get("memory")

    if memory and hasattr(memory, "traces") and memory.traces:
        recent = memory.traces[-10:]
        st.table(
            [
                {
                    "tick": t.tick,
                    "Z": round(t.Z, 3),
                    "coherence": round(t.coherence, 3),
                    "stability": round(t.stability, 3),
                    "frame": t.frame_signature,
                    "tags": ", ".join(t.tags),
                }
                for t in recent
            ]
        )
    else:
        st.caption("No memory traces recorded yet.")

    # ---------------------------------
    # FINAL STATE
    # ---------------------------------
    st.subheader("Final State")
    st.json(data)