# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py

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
    # METRICS (CURRENT)
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
    # METRIC EVOLUTION (TRUE PROGRESSION)
    # -------------------------------------------------
    st.subheader("Metric Evolution")

    hist = state["metric_history"]

    if len(hist["ticks"]) > 1:
        fig, ax = plt.subplots(figsize=(9, 4))

        ax.plot(hist["ticks"], hist["Z"], label="Z (Fragmentation)")
        ax.plot(hist["ticks"], hist["Coherence"], label="Coherence")
        ax.plot(hist["ticks"], hist["Stability"], label="Stability")

        # Crystallisation overlays
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
        ax.set_ylim(0, 1)
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)
    else:
        st.info("Run a few ticks to see metric evolution.")

    # -------------------------------------------------
    # FINAL STATE
    # -------------------------------------------------
    st.subheader("Final State")
    st.json(data)