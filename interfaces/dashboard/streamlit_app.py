# interfaces/dashboard/streamlit_app.py
"""
A7DO — Sandy’s Law Dashboard
v1.1 with Sidebar Menu + Memory Visibility
"""

import streamlit as st


def main(snapshot):
    # --------------------------------------------------
    # Page config
    # --------------------------------------------------
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

    # Lazy imports to avoid circulars
    from bootstrap import (
        inject_demo_frame,
        add_fragment,
        close_frame,
        tick_system,
    )

    # Build a stable state reference
    data = snapshot()
    state = snapshot.__closure__[0].cell_contents if snapshot.__closure__ else None

    # NOTE:
    # We do NOT mutate state here directly; actions call bootstrap helpers

    if st.sidebar.button("▶ Open Demo Frame"):
        try:
            inject_demo_frame(state)
        except Exception as e:
            st.sidebar.warning(str(e))

    if st.sidebar.button("➕ Add Fragment"):
        try:
            add_fragment(state)
        except Exception as e:
            st.sidebar.warning(str(e))

    if st.sidebar.button("⏹ Close Frame"):
        try:
            close_frame(state)
        except Exception as e:
            st.sidebar.warning(str(e))

    st.sidebar.divider()

    if st.sidebar.button("⏱ Tick"):
        try:
            tick_system(state)
        except Exception as e:
            st.sidebar.warning(str(e))

    st.sidebar.divider()
    st.sidebar.markdown("### Status")

    # --------------------------------------------------
    # Pull fresh snapshot after actions
    # --------------------------------------------------
    data = snapshot()

    # ==================================================
    # SYSTEM OVERVIEW
    # ==================================================
    st.subheader("System Overview")

    st.json(
        {
            "ticks": data["ticks"],
            "roles": data.get("roles", []),
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
            "Memory crystallising: system has remained inside allowed region "
            "long enough to persist structure."
        )
    else:
        st.info(
            "No memory crystallised yet. "
            "System is either outside regulation gates or has not remained stable long enough."
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


# --------------------------------------------------
# Entry point (for direct run)
# --------------------------------------------------
if __name__ == "__main__":
    from bootstrap import build_system

    _, snapshot, _ = build_system()
    main(snapshot)