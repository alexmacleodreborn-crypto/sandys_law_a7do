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

    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }
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
    m1.metric("Z", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # ---------------------------------
    # RECORD HISTORY
    # ---------------------------------
    if state["last_recorded_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["last_recorded_tick"] = data["ticks"]

    # ---------------------------------
    # METRIC EVOLUTION
    # ---------------------------------
    st.subheader("Metric Evolution")
    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")

    ax.set_ylim(0.0, 1.05)
    ax.set_xlabel("Tick")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # GATES (READ ONLY)
    # ---------------------------------
    st.subheader("Gate Status (Read-Only)")

    gates = data.get("gates", {})
    if gates:
        st.table([
            {
                "gate": name,
                "score": round(info["score"], 3),
                "open": info["open"],
                "reason": info["reason"],
            }
            for name, info in gates.items()
        ])
    else:
        st.caption("No gate data available.")

    # ---------------------------------
    # PREFERENCES (READ ONLY)
    # ---------------------------------
    st.subheader("Preference Bias (Top Contexts)")
    if data.get("preference_top"):
        st.table(data["preference_top"])
    else:
        st.caption("No preference data yet.")