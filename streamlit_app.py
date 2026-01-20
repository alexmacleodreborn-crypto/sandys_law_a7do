# interfaces/dashboard/streamlit_app.py

import streamlit as st


def main(system_snapshot_provider):
    st.set_page_config(page_title="A7DO Dashboard", layout="wide")
    st.title("A7DO — Sandy’s Law System Dashboard")

    # -----------------------------------------
    # SESSION STATE (UI ONLY)
    # -----------------------------------------
    if "demo_frames" not in st.session_state:
        st.session_state.demo_frames = []

    # -----------------------------------------
    # CONTROL PANEL
    # -----------------------------------------
    st.sidebar.header("Controls")

    if st.sidebar.button("➕ Create Demo Frame"):
        st.session_state.demo_frames.append(
            {
                "fragments": [],
                "metadata": {},
            }
        )

    if st.sidebar.button("➕ Add Demo Fragment"):
        if st.session_state.demo_frames:
            st.session_state.demo_frames[-1]["fragments"].append(
                {"kind": "demo", "payload": {"source": "ui"}}
            )

    # -----------------------------------------
    # SNAPSHOT
    # -----------------------------------------
    snapshot = system_snapshot_provider()

    # Inject demo frames safely (no core mutation)
    snapshot["frames"] = st.session_state.demo_frames

    # -----------------------------------------
    # SYSTEM OVERVIEW
    # -----------------------------------------
    st.subheader("System Overview")
    st.json(
        {
            "roles": snapshot.get("roles", []),
            "frame_count": len(snapshot.get("frames", [])),
        }
    )

    # -----------------------------------------
    # METRICS
    # -----------------------------------------
    if "metrics" in snapshot:
        st.subheader("Metrics")
        for k, v in snapshot["metrics"].items():
            st.progress(min(1.0, float(v)))
            st.caption(f"{k}: {float(v):.2f}")

    # -----------------------------------------
    # FRAME INSPECTOR
    # -----------------------------------------
    st.subheader("Frame Inspector")

    frames = snapshot.get("frames", [])
    if not frames:
        st.info("No frames available")
    else:
        for i, frame in enumerate(frames):
            with st.expander(f"Frame {i}"):
                st.write("Fragments:", len(frame.get("fragments", [])))
                st.json(frame.get("metadata", {}))