# sandys_law_a7do/interfaces/dashboard/dashboard_ui.py
"""
A7DO — Sandy’s Law Dashboard UI
Stability timeline corrected (structural vs temporal signals)
"""

import streamlit as st
from dataclasses import asdict
import pandas as pd

from sandys_law_a7do.bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)


def render_dashboard(state, snapshot):
    # ==================================================
    # SESSION STATE (UI ONLY)
    # ==================================================

    if "timeline" not in st.session_state:
        st.session_state.timeline = []

    if "last_memory_count" not in st.session_state:
        st.session_state.last_memory_count = 0

    if "crystallisation_ticks" not in st.session_state:
        st.session_state.crystallisation_ticks = []

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

    # ==================================================
    # SNAPSHOT
    # ==================================================

    data = snapshot()
    metrics = data["metrics"]

    # ==================================================
    # RECORD TIMELINE POINT (ONCE PER TICK ONLY)
    # ==================================================

    last_tick = (
        st.session_state.timeline[-1]["tick"]
        if st.session_state.timeline
        else None
    )

    if last_tick != data["ticks"]:
        st.session_state.timeline.append(
            {
                "tick": data["ticks"],
                "Z": metrics["Z"],
                "Coherence": metrics["Coherence"],
                "Stability": metrics["Stability"],
            }
        )

    # Keep UI memory bounded
    st.session_state.timeline = st.session_state.timeline[-200:]

    # ==================================================
    # DETECT CRYSTALLISATION EVENT
    # ==================================================

    if data["memory_count"] > st.session_state.last_memory_count:
        st.session_state.crystallisation_ticks.append(data["ticks"])

    st.session_state.last_memory_count = data["memory_count"]

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
    st.caption(f"Z (Fragmentation — structural): {metrics['Z']:.3f}")

    st.progress(float(metrics["Coherence"]))
    st.caption(f"Coherence: {metrics['Coherence']:.3f}")

    st.progress(float(metrics["Stability"]))
    st.caption(f"Stability (temporal): {metrics['Stability']:.3f}")

    # ==================================================
    # STABILITY TIMELINE (CORRECTED)
    # ==================================================

    st.subheader("Stability Timeline")

    st.caption(
        "Z changes only when fragments change. "
        "Ticks evaluate stability but do not alter structure."
    )

    timeline = st.session_state.timeline

    if len(timeline) > 1:
        df = pd.DataFrame(timeline).set_index("tick")

        st.line_chart(df[["Z", "Coherence", "Stability"]])

        if st.session_state.crystallisation_ticks:
            st.caption(
                f"Crystallisation occurred at ticks: "
                f"{st.session_state.crystallisation_ticks}"
            )
    else:
        st.info("Tick the system to build a timeline")

    # ==================================================
    # REGULATION
    # ==================================================

    st.subheader("Regulation Decision")

    reg = data["regulation"]
    if hasattr(reg, "__dataclass_fields__"):
        st.json(asdict(reg))
    else:
        st.json(reg)

    # ==================================================
    # MEMORY
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

    traces = state["memory"].all()

    if not traces:
        st.info("No crystallised memory yet")
    else:
        recent = traces[-5:]
        st.table(
            [
                {
                    "tick": t.tick,
                    "Z": round(t.Z, 3),
                    "coherence": round(t.coherence, 3),
                    "stability": round(t.stability, 3),
                    "frame": t.frame_signature,
                    "weight": round(t.weight, 3),
                }
                for t in recent
            ]
        )

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