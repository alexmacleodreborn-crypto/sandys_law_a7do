# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py

import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)

# =====================================================
# DASHBOARD RENDER
# =====================================================

def render_dashboard(state, snapshot):
    st.set_page_config(page_title="A7DO — Sandy’s Law", layout="wide")
    st.title("A7DO — Sandy’s Law System Dashboard")

    # -------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------
    data = snapshot()

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
    # METRICS
    # -------------------------------------------------
    metrics = data["metrics"]

    st.subheader("Metrics")
    col1, col2, col3 = st.columns(3)
    col1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    col2.metric("Coherence", round(metrics["Coherence"], 3))
    col3.metric("Stability", round(metrics["Stability"], 3))

    # -------------------------------------------------
    # CONTROLS
    # -------------------------------------------------
    st.subheader("Controls")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        if st.button("🆕 New Frame"):
            inject_demo_frame(state)

    with c2:
        if st.button("➕ Add Fragment"):
            add_fragment_by_kind(state, "demo")

    with c3:
        if st.button("⏹ Close Frame"):
            close_frame(state)

    with c4:
        if st.button("⏭ Tick"):
            tick_system(state)

    # -------------------------------------------------
    # METRIC HISTORY (UNCHANGED)
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
        label="Z (Fragmentation)"
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Coherence"],
        label="Coherence"
    )
    ax.plot(
        state["history"]["ticks"],
        state["history"]["Stability"],
        label="Stability"
    )

    # 🔹 Crystallisation overlay (EVENT, not metric)
    cryst_ticks = state.get("crystallisation_ticks", [])
    for i, t in enumerate(cryst_ticks):
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