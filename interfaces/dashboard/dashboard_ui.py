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
            "Attention": [],
            "Load": [],
        }

    if "record_history" not in state:
        state["record_history"] = False

    if "last_recorded_tick" not in state:
        state["last_recorded_tick"] = None

    st.title("A7DO — Sandy’s Law System Dashboard")

    # ---------------------------------
    # CONTROLS
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
        state["record_history"] = True

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)
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
    m1, m2, m3, m4, m5, m6 = st.columns(6)
    m1.metric("Z", round(metrics.get("Z", 0.0), 3))
    m2.metric("Coherence", round(metrics.get("Coherence", 0.0), 3))
    m3.metric("Stability", round(metrics.get("Stability", 0.0), 3))
    m4.metric("Load", round(metrics.get("Load", 0.0), 3))
    m5.metric("Attention", round(metrics.get("Attention", 0.0), 3))
    m6.metric("PredErr", round(float(state.get("prediction_error", 0.0)), 3))

    # ---------------------------------
    # RECORD HISTORY (SAFE)
    # ---------------------------------
    if state["record_history"] and state["last_recorded_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics.get("Z", 0.0))
        state["history"]["Coherence"].append(metrics.get("Coherence", 0.0))
        state["history"]["Stability"].append(metrics.get("Stability", 0.0))
        state["history"]["Load"].append(metrics.get("Load", 0.0))
        state["history"]["Attention"].append(metrics.get("Attention", 0.0))

        state["last_recorded_tick"] = data["ticks"]
        state["record_history"] = False

    # ---------------------------------
    # METRIC EVOLUTION PLOT
    # ---------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z", color="red")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence", color="blue")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability", color="green")
    ax.plot(state["history"]["ticks"], state["history"]["Load"], label="Load", color="orange", linestyle=":")
    ax.plot(state["history"]["ticks"], state["history"]["Attention"], label="Attention", color="purple", linestyle="--")

    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # ---------------------------------
    # PREFERENCE STATUS (READ-ONLY)
    # ---------------------------------
    st.subheader("Preference (Read-only Bias)")

    last_up = state.get("last_preference_update")
    if last_up:
        st.json(last_up)
    else:
        st.caption("No preference update yet (tick to generate one).")

    pref_top = data.get("preference_top", [])
    if pref_top:
        st.table(pref_top)
    else:
        st.caption("No preference contexts yet (needs repeated ticks/episodes).")

    # ---------------------------------
    # MEMORY TIMELINE (READ-ONLY)
    # ---------------------------------
    st.subheader("Memory Timeline (Recent)")
    memory = state.get("memory")
    if memory and hasattr(memory, "traces") and memory.traces:
        recent = memory.traces[-10:]
        st.table([
            {
                "tick": t.tick,
                "Z": round(t.Z, 3),
                "coherence": round(t.coherence, 3),
                "stability": round(t.stability, 3),
                "frame": t.frame_signature,
                "tags": ", ".join(t.tags),
            }
            for t in recent
        ])
    else:
        st.caption("No memory traces recorded yet (close a frame to commit).")

    st.subheader("Final State")
    st.json(data)