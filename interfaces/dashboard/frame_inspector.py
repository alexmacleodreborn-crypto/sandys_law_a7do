# sandys_law_a7do/interfaces/dashboard/frame_inspector.py

import streamlit as st

def render_frame_inspector(frame_store, ledger):
    st.subheader("🧠 Frame Inspector")

    # --- Active Frame ---
    st.markdown("### Active Frame")
    if frame_store.active:
        st.success("Frame ACTIVE")
        st.json({
            "domain": frame_store.active.domain,
            "label": frame_store.active.label,
            "fragments": len(frame_store.active.fragments)
        })
    else:
        st.warning("No active frame")

    # --- Fragment Stream ---
    st.markdown("### 📡 Fragment Stream")
    if frame_store.active:
        for frag in frame_store.active.fragments:
            st.code(f"{frag.domain} :: {frag.action} :: {frag.payload}")
    else:
        st.caption("No fragments")

    # --- Timeline ---
    st.markdown("### 🧾 Frame Timeline")
    for i, frame in enumerate(ledger.frames):
        with st.expander(f"Frame {i+1}: {frame.domain} / {frame.label}"):
            for frag in frame.fragments:
                st.write(f"- {frag.action} | {frag.payload}")
