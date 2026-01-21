import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import open_frame, add_fragment, close_frame
from sandys_law_a7do.engine.tick_engine import step_tick


def render_dashboard(state, snapshot):
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # INIT HISTORY (ONCE)
    # ---------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }

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

    if c2.button("➕ Add Fragment"):
        add_fragment(state)

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)   # ✅ ONLY place tick is called

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
    m1, m2, m3 = st.columns(3)
    m1.metric("Z (Fragmentation)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))

    # ---------------------------------
    # RECORD HISTORY (PURE APPEND)
    # ---------------------------------
    state["history"]["ticks"].append(data["ticks"])
    state["history"]["Z"].append(metrics["Z"])
    state["history"]["Coherence"].append(metrics["Coherence"])
    state["history"]["Stability"].append(metrics["Stability"])

    # ---------------------------------
    # METRIC EVOLUTION PLOT (IMPROVED)
    # ---------------------------------
    st.subheader("Metric Evolution")

    fig, ax1 = plt.subplots(figsize=(9, 4))

    # Primary axis: Z (Fragmentation)
    ax1.plot(
        state["history"]["ticks"],
        state["history"]["Z"],
        label="Z (Fragmentation)",
        color="tab:red",
        linewidth=2,
    )
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Fragmentation (Z)")
    ax1.set_ylim(0.0, 1.0)

    # Secondary axis: Coherence & Stability
    ax2 = ax1.twinx()
    ax2.plot(
        state["history"]["ticks"],
        state["history"]["Coherence"],
        label="Coherence",
        color="tab:blue",
        linewidth=2,
    )
    ax2.plot(
        state["history"]["ticks"],
        state["history"]["Stability"],
        label="Stability",
        color="tab:green",
        linewidth=2,
    )
    ax2.set_ylabel("Coherence / Stability")
    ax2.set_ylim(0.0, 1.05)

    # Combined legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="lower left")

    ax1.grid(True)

    st.pyplot(fig)

    # ---------------------------------
    # FINAL STATE
    # ---------------------------------
    st.subheader("Final State")
    st.json(data)