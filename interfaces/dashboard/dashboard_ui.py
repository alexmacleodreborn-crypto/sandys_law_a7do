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
            "Attention": [],
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
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics.get("Load", 0.0), 3))

    # ---------------------------------
    # EXTRACT LATEST ATTENTION (SAFE)
    # ---------------------------------
    latest_attention = None
    frame = data["active_frame"]

    if frame and frame.fragments:
        last_frag = frame.fragments[-1]
        latest_attention = last_frag.payload.get("attention")

    # ---------------------------------
    # RECORD HISTORY (SAFE + FRAME AWARE)
    # ---------------------------------
    should_record = data["active_frame"] is not None or state["record_history"]

    if should_record and state["last_recorded_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["history"]["Attention"].append(
            float(latest_attention) if latest_attention is not None else None
        )

        state["last_recorded_tick"] = data["ticks"]
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
        color="green",
    )

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.set_ylim(0.0, 1.05)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # ATTENTION EVOLUTION
    # ---------------------------------
    st.subheader("Attention Signal")

    if any(a is not None for a in state["history"]["Attention"]):
        fig2, ax2 = plt.subplots(figsize=(9, 3))

        ax2.plot(
            state["history"]["ticks"],
            state["history"]["Attention"],
            label="Attention",
            color="purple",
        )

        ax2.set_xlabel("Tick")
        ax2.set_ylabel("Attention")
        ax2.legend()
        ax2.grid(True)

        st.pyplot(fig2)
    else:
        st.caption("Attention will appear once fragments are generated.")

    # ---------------------------------
    # PREFERENCE STATE (READ-ONLY)
    # ---------------------------------
    st.subheader("Preference State")

    if data.get("preference_top"):
        st.table(data["preference_top"])
    else:
        st.caption("No preferences recorded yet.")

    if data.get("last_preference_update"):
        st.markdown("**Last Preference Update**")
        st.json(data["last_preference_update"])

    # ---------------------------------
    # MEMORY TIMELINE
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
        st.caption("No memory traces recorded yet.")

    # ---------------------------------
    # FINAL STATE (DEBUG)
    # ---------------------------------
    st.subheader("Final State (Debug)")
    st.json(data)