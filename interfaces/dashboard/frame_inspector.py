# interfaces/dashboard/frame_inspector.py

import streamlit as st


def render_frame_inspector(frames):
    """
    frames: iterable of Frame objects
    """
    st.subheader("Frame Inspector")

    if not frames:
        st.info("No frames available")
        return

    for i, frame in enumerate(frames):
        with st.expander(f"Frame {i}"):
            st.write("Fragments:", len(frame.fragments))
            st.json(frame.metadata if hasattr(frame, "metadata") else {})
