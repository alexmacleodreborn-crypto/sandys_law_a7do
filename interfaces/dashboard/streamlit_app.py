# sandys_law_a7do/interfaces/dashboard/streamlit_app.py
"""
A7DO — Sandy’s Law Dashboard
v1.1 — Menu + Memory Visibility
"""

import streamlit as st

# --------------------------------------------------
# IMPORTANT:
# Always import through the PACKAGE
# --------------------------------------------------
from sandys_law_a7do.bootstrap import (
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)


def main(snapshot):
    st.set_page_config(
        page_title="A7DO — Sandy’s Law Dashboard",
        layout="wide",
    )

    st.title("A7DO — Sandy’s Law System Dashboard")

    # --------------------------------------------------
    # Sidebar menu
    # --------------------------------------------------
    st.sidebar.title("A7DO Control Panel")

    st.sidebar.markdown("### Frame Controls")

    # Get access to the shared state via snapshot closure
    state = snapshot.__closure__[0].cell_contents

    if st.sidebar.button("▶ New Frame"):
    # Enforce single-frame invariant
    if state["frames"].active is not None:
        close_frame(state)
    inject_demo_frame(state)

    if st.sidebar.button("➕ Add Fragment"):
        add_fragment_by_kind(state, "demo")

    if st.sidebar.button("⏹ Close Frame"):
        close_frame(state)

    st.sidebar.divider()

    if st.sidebar.button("⏱ Tick"):
        tick_system(state)

    st.sidebar.divider()
    st.sidebar.markdown("### Status")

    # --------------------------------------------------
    # Pull fresh snapshot
    # --------------------------------------------------
    data = snapshot()

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

    metrics = data["metrics"]

    st.progress(float(metrics["Z"]))
    st.caption(f"Z (Fragmentation): {metrics['Z']:.3f}")

    st.progress(float(metrics["Coherence"]))
    st.caption(f"Coherence: {metrics['Coherence']:.3f}")

    st.progress(float(metrics["Stability"]))
    st.caption(f"Stability: {metrics['Stability']:.3f}")

    # ==================================================
    # REGULATION
    # ==================================================
    st.subheader("Regulation")
    st.json(data["regulation"])

    # ==================================================
    # MEMORY (v1.1)
    # ==================================================
    st.subheader("Structural Memory")

    memory_count = data.get("memory_count", 0)

    st.metric(
        label="Structural Memory Count",
        value=int(memory_count),
    )

    if memory_count > 0:
        st.success(
            "Memory crystallising: system remained inside allowed region "
            "long enough to persist structure."
        )
    else:
        st.info(
            "No memory crystallised yet "
            "(outside gates or insufficient persistence)."
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