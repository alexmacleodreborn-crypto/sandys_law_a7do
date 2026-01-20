# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py
"""
A7DO — Sandy’s Law Dashboard UI
Adds Stability Timeline Plot (v1.1)
"""

import streamlit as st
from dataclasses import asdict

from sandys_law_a7do.bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)


def render_dashboard(state, snapshot):
    # ==================================================
    # SESSION STORAGE FOR TIMELINE (UI-ONLY)
    # ==================================================

    if "timeline" not in st.session_state:
        st.session_state.timeline = []

    # ==================================================
    # SIDEBAR CONTROLS
    # ==================================================

    st.sidebar.title("A7DO Control Panel")

    st.sidebar.markdown("### Frame Lifecycle")

    if st.sidebar.button("▶ New Frame"):
        if state["frames"].active is not None:
            close_frame(state)
        inject_demo_frame(state)

    if st.sidebar.button("➕ Add Fragment"):
        if state["frames"].active is None:
            inject_demo_frame(state)
        add_fragment_by_kind(state, "demo")

    if st.sidebar.button("⏹ Close Frame"):
        close_frame(state)

    st.sidebar.divider()

    if st.sidebar.button("⏱ Tick"):
        tick_system(state)

    # --------------------------------------------------
    # SNAPSHOT AFTER ACTIONS
    # --------------------------------------------------

    data = snapshot()
    metrics = data["metrics"]

    # ==================================================
    # RECORD TIMELINE POINT
    # ==================================================

    st.session_state.timeline.append(
        {
            "tick": data["ticks"],
            "Z": metrics["Z"],
            "Coherence": metrics["Coherence"],
            "Stability": metrics["Stability"],
        }
    )

    # Limit memory to last N ticks (UI only)
    MAX_POINTS = 100
    st.session_state.timeline = st.session_state.timeline[-MAX_POINTS:]

    # ==================================================
    # SYSTEM OVERVIEW
    # ==================================================

    st.subheader("System Overview")

    st.json(
        {
            "ticks": data["ticks"],
            "active_frame": (
                {
                    "domain": data["active_frame"].domain,
                    "label": data["active_frame"].label,
                    "fragments": len(data["active_frame"].fragments),
                }
                if data["active_frame"]
                else None
            ),
        }
    )

    # ==================================================
    # METRICS
    # ==================================================

    st.subheader("Metrics")

    st.progress(float(metrics["Z"]))
    st.caption(f"Z (Fragmentation): {metrics['Z']:.3f}")

    st.progress(float(metrics["Coherence"]))
    st.caption(f"Coherence: {metrics['Coherence']:.3f}")

    st.progress(float(metrics["Stability"]))
    st.caption(f"Stability: {metrics['Stability']:.3f}")

    # ==================================================
    # STABILITY TIMELINE (NEW)
    # ==================================================

    st.subheader("Stability Timeline")

    timeline = st.session_state.timeline

    if len(timeline) > 1:
        st.line_chart(
            {
                "Z": [p["Z"] for p in timeline],
                "Coherence": [p["Coherence"] for p in timeline],
                "Stability": [p["Stability"] for p in timeline],
            }
        )
        st.caption("Z (fragmentation), Coherence, and Stability over ticks")
    else:
        st.info("Tick the system to build a timeline")

    # ==================================================
    # REGULATION (SAFE SERIALISATION)
    # ==================================================

    st.subheader("Regulation Decision")

    reg = data["regulation"]
    if hasattr(reg, "__dataclass_fields__"):
        st.json(asdict(reg))
    else:
        st.json(reg)

    # ==================================================
    # MEMORY SUMMARY
    # ==================================================

    st.subheader("Structural Memory")

    st.metric(
        label="Crystallised Memory Count",
        value=data["memory_count"],
    )

    # ==================================================
    # RECENT MEMORY TRACES
    # ==================================================

    st.subheader("Recent Memory Traces")

    memory = state["memory"]
    traces = memory.all()

    if not traces:
        st.info("No crystallised memory yet")
    else:
        recent = traces[-5:]

        table = []
        for t in recent:
            table.append(
                {
                    "tick": t.tick,
                    "Z": round(t.Z, 3),
                    "coherence": round(t.coherence, 3),
                    "stability": round(t.stability, 3),
                    "frame": t.frame_signature,
                    "weight": round(t.weight, 3),
                }
            )

        st.table(table)

    # ==================================================
    # FRAME INSPECTOR
    # ==================================================

    st.subheader("Frame Inspector")

    if data["active_frame"]:
        frame = data["active_frame"]
        st.write(f"**Domain:** {frame.domain}")
        st.write(f"**Label:** {frame.label}")
        st.write(f"**Fragments:** {len(frame.fragments)}")

        for i, frag in enumerate(frame.fragments):
            st.code(f"{i}: {frag.kind}")
    else:
        st.info("No active frame")