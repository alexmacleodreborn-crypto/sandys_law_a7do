# interfaces/dashboard/streamlit_app.py
"""
A7DO — Sandy’s Law Dashboard
v1.1: Memory visibility added (read-only)
"""

import streamlit as st


def main(snapshot):
    # --------------------------------------------------
    # Page config
    # --------------------------------------------------
    st.set_page_config(
        page_title="A7DO — Sandy’s Law System Dashboard",
        layout="wide",
    )

    st.title("A7DO — Sandy’s Law System Dashboard")

    # --------------------------------------------------
    # Pull system snapshot
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
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    from bootstrap import build_system

    _, snapshot, _ = build_system()
    main(snapshot)