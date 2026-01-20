# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py
"""
A7DO — Sandy’s Law Dashboard UI
Render-only module (Option A: relative imports)
"""

import streamlit as st
import matplotlib.pyplot as plt

# RELATIVE IMPORTS (CRITICAL)
from ...bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)


# =====================================================
# DASHBOARD RENDER
# =====================================================

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
    # CONTROLS
    # -------------------------------------------------
    st.subheader("Controls")
    b1, b2, b3, b4 = st.columns(4)

    if b1.button("🆕 New Frame"):
        inject_demo_frame(state)

    if b2.button("➕ Add Fragment"):
        add_fragment_by_kind(state, "demo")

    if b3.button("⏹ Close Frame"):
        close_frame(state)

    if b4.button("⏭ Tick"):
        tick_system(state)

    # -------------------------------------------------
    # METRIC HISTORY (PRESERVE EXISTING BEHAVIOUR)
    # -------------------------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }

    state["history"]["ticks"].append(data["ticks"])
    state["history"]["Z"].append(metrics["Z"])
    state["history"]["Coherence"].append(metrics["Coherence"])
    state["history"]["Stability"].append(metrics["Stability"])

    # -------------------------------------------------
    # METRIC EVOLUTION + CRYSTALLISATION OVERLAY
    # -------------------------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(
        state["history"]["ticks"],
        state["history"]["Z"],
        label="Z (Fragmentation)",
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Coherence"],
        label="Coherence",
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Stability"],
        label="Stability",
    )

    # Crystallisation markers (event-based)
    for i, t in enumerate(state.get("crystallisation_ticks", [])):
        ax.axvline(
            x=t,
            linestyle="--",
            linewidth=1.5,
            alpha=0.7,
            label="Crystallisation" if i == 0 else None,
        )

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