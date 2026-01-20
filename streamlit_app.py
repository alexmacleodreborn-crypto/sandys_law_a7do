# interfaces/dashboard/streamlit_app.py

import streamlit as st
from frames.frame import Frame
from frames.fragment import Fragment


def main(system_snapshot_provider):
    st.set_page_config(page_title="A7DO Dashboard", layout="wide")
    st.title("A7DO — Sandy’s Law System Dashboard")

    # -----------------------------------------
    # SESSION STATE (UI ONLY)
    # -----------------------------------------
    if "frames" not in st.session_state:
        st.session_state.frames = []

    # -----------------------------------------
    # CONTROL PANEL
    # -----------------------------------------
    st.sidebar.header("Controls")

    if st.sidebar.button("➕ Create Frame"):
        st.session_state.frames.append(Frame())

    if st.sidebar.button("➕ Add Fragment"):
        if st.session_state.frames:
            frag = Fragment(kind="demo", payload={"source": "ui"})
            st.session_state.frames[-1].add(frag)

    # -----------------------------------------
    # SNAPSHOT (override frames safely)
    # -----------------------------------------
    snapshot = system_snapshot_provider()
    snapshot["frames"] = st.session_state.frames

    # -----------------------------------------
    # OVERVIEW
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
            st.caption(f"{k}: {v:.2f}")

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
                st.write("Fragments:", len(frame.fragments))
                st.json(frame.metadata)