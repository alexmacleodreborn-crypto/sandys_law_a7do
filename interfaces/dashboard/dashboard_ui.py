import streamlit as st
import matplotlib.pyplot as plt

from ...bootstrap import (
    inject_demo_frame,
    close_frame,
    tick_system,
)

def render_dashboard(state, snapshot):

    st.title("A7DO — Sandy’s Law System Dashboard")

    # -------------------------------------------------
    # CONTROLS (ACTIONS FIRST)
    # -------------------------------------------------
    st.subheader("Controls")
    c1, c2, c3 = st.columns(3)

    if c1.button("🆕 New Frame"):
        inject_demo_frame(state)

    if c2.button("⏹ Close Frame"):
        close_frame(state)

    if c3.button("⏭ Tick"):
        tick_system(state)

    # -------------------------------------------------
    # SNAPSHOT (AFTER ACTIONS)
    # -------------------------------------------------
    data = snapshot()
    m = data["metrics"]

    # -------------------------------------------------
    # OVERVIEW
    # -------------------------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": (
            f"{data['active_frame'].domain}:{data['active_frame'].label}"
            if data["active_frame"] else "none"
        ),
        "memory_count": data["memory_count"],
    })

    # -------------------------------------------------
    # METRICS (CURRENT)
    # -------------------------------------------------
    st.subheader("Metrics")
    a, b, c = st.columns(3)
    a.metric("Z", round(m["Z"], 3))
    b.metric("Coherence", round(m["Coherence"], 3))
    c.metric("Stability", round(m["Stability"], 3))

    # -------------------------------------------------
    # METRIC EVOLUTION (REAL)
    # -------------------------------------------------
    st.subheader("Metric Evolution")

    hist = state["metric_history"]

    if len(hist["ticks"]) > 1:
        fig, ax = plt.subplots(figsize=(9, 4))

        ax.plot(hist["ticks"], hist["Z"], label="Z")
        ax.plot(hist["ticks"], hist["Coherence"], label="Coherence")
        ax.plot(hist["ticks"], hist["Stability"], label="Stability")

        for i, t in enumerate(state["crystallisation_ticks"]):
            ax.axvline(
                t,
                linestyle="--",
                alpha=0.6,
                label="Crystallisation" if i == 0 else None,
            )

        ax.set_ylim(0, 1)
        ax.set_xlabel("Tick")
        ax.legend()
        ax.grid(True)
        st.pyplot(fig)
    else:
        st.info("Press Tick a few times to see dynamics.")

    # -------------------------------------------------
    # FINAL SNAPSHOT
    # -------------------------------------------------
    st.subheader("Final Snapshot")
    st.json(data)