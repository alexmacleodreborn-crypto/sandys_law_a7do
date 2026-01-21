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
    # INIT HISTORY
    # ---------------------------------
    if "history" not in state:
        state["history"] = {"ticks": [], "Z": [], "Coherence": [], "Stability": []}
        state["last_tick"] = None

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Sandy’s Law System Dashboard")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Fragment"):
        add_fragment(state)

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # SNAPSHOT
    # ---------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": (
            f"{data['active_frame'].domain}:{data['active_frame'].label}"
            if data["active_frame"] else "none"
        ),
        "memory_count": data["memory_count"],
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    m1, m2, m3 = st.columns(3)
    m1.metric("Z", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))

    # ---------------------------------
    # HISTORY (SAFE)
    # ---------------------------------
    if state["last_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["last_tick"] = data["ticks"]

    # ---------------------------------
    # PLOT
    # ---------------------------------
    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")
    ax.set_ylim(0, 1.05)
    ax.legend()
    ax.grid(True)
    st.pyplot(fig)

    # ---------------------------------
    # GATES
    # ---------------------------------
    st.subheader("Gates")
    gates = data.get("gates", {})

    if gates:
        st.table([
            {
                "gate": name,
                "open": info["open"],
                "score": info["score"],
                "pressure": info["pressure"],
                "reason": info["reason"],
            }
            for name, info in gates.items()
        ])
    else:
        st.caption("No gate data yet.")

    # ---------------------------------
    # MEMORY
    # ---------------------------------
    st.subheader("Memory (Recent)")
    memory = state.get("memory")

    if memory and memory.traces:
        st.table([
            {
                "tick": t.tick,
                "Z": round(t.Z, 3),
                "coherence": round(t.coherence, 3),
                "stability": round(t.stability, 3),
                "frame": t.frame_signature,
                "tags": ", ".join(t.tags),
            }
            for t in memory.traces[-10:]
        ])
    else:
        st.caption("No memory traces yet.")