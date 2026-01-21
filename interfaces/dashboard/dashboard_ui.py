"""
A7DO — Sandy’s Law Dashboard UI
Render-only module
"""

import streamlit as st
import matplotlib.pyplot as plt

from ...bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)


def render_dashboard(state, snapshot):
    data = snapshot()
    metrics = data["metrics"]

    st.title("A7DO — Sandy’s Law System Dashboard")

    # -------------------------------------------------
    # SYSTEM OVERVIEW
    # -------------------------------------------------
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

    # -------------------------------------------------
    # METRICS
    # -------------------------------------------------
    st.subheader("Metrics")
    c1, c2, c3 = st.columns(3)
    c1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    c2.metric("Coherence", round(metrics["Coherence"], 3))
    c3.metric("Stability", round(metrics["Stability"], 3))

    # -------------------------------------------------
    # CONTROLS (ORDER MATTERS)
    # -------------------------------------------------
    st.subheader("Controls")
    b1, b2, b3, b4 = st.columns(4)

    if b1.button("🆕 New Frame"):
        inject_demo_frame(state)

    if b2.button("➕ Add Fragment"):
        if state["frames"].active is None:
            st.warning("No active frame. Open a frame first.")
        else:
            add_fragment_by_kind(state, "demo")

    if b3.button("⏹ Close Frame"):
        close_frame(state)

    if b4.button("⏭ Tick"):
        tick_system(state)

    # -------------------------------------------------
    # METRIC EVOLUTION
    # -------------------------------------------------
    st.subheader("Metric Evolution")

    hist = state["metric_history"]

    fig, ax = plt.subplots(figsize=(9, 4))
    ax.plot(hist["ticks"], hist["Z"], label="Z (Fragmentation)")
    ax.plot(hist["ticks"], hist["Coherence"], label="Coherence")
    ax.plot(hist["ticks"], hist["Stability"], label="Stability")

    for t in state["crystallisation_ticks"]:
        ax.axvline(t, linestyle="--", alpha=0.6)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # -------------------------------------------------
    # FINAL STATE
    # -------------------------------------------------
    st.subheader("Final State")
    st.json(data)