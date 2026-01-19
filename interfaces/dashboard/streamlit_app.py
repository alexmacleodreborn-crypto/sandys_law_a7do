from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st
import pandas as pd

# ============================================================
# Ensure repo root is on sys.path
# File path:
# sandys_law_a7do/interfaces/dashboard/streamlit_app.py
# ============================================================

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
# Core imports (package-safe)
# ============================================================

from sandys_law_a7do.frames import FrameStore
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.integration.phase2_loop import Phase2Loop
from sandys_law_a7do.identity import IdentityStore, IdentityEngine

# ============================================================
# Streamlit setup
# ============================================================

st.set_page_config(
    page_title="A7DO — Frame-Based Mind",
    layout="wide",
)

st.title("A7DO — Frame-Based Cognitive System")
st.caption("No time • Frames only • Embodied cognition")

# ============================================================
# Session State Initialization
# ============================================================

if "frame_store" not in st.session_state:
    st.session_state.frame_store = FrameStore()
    st.session_state.frame_store.begin()

if "closed_frames" not in st.session_state:
    st.session_state.closed_frames = []

if "phase2" not in st.session_state:
    st.session_state.phase2 = Phase2Loop()

if "identity_store" not in st.session_state:
    st.session_state.identity_store = IdentityStore("data/identity/identity.json")
    st.session_state.identity_engine = IdentityEngine()
    st.session_state.identity = st.session_state.identity_store.load()

# ============================================================
# Controls — Frame Interaction
# ============================================================

st.subheader("Frame Interaction")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬆️ Contact Top", key="btn_contact_top"):
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="contact",
                payload={"region": "top"},
            )
        )

with col2:
    if st.button("🔥 Thermal Bottom", key="btn_thermal_bottom"):
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="thermal",
                payload={"region": "bottom", "delta": 0.7},
            )
        )

with col3:
    if st.button("💥 Force Left", key="btn_force_left"):
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="force",
                payload={"region": "left", "force": 6.0},
            )
        )

# ============================================================
# Close Frame
# ============================================================

if st.button("⏹️ Close Frame", key="btn_close_frame"):
    closed = st.session_state.frame_store.close()

    if closed:
        st.session_state.closed_frames.append(closed)

        # ---------------- Phase processing ----------------
        entry, pref, trace = st.session_state.phase2.step(
            frames=[closed]
        )

        # ---------------- Identity update ----------------
        st.session_state.identity = st.session_state.identity_engine.update(
            st.session_state.identity,
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
            prediction_error=entry.prediction_error_l1,
            ownership_consistency=1.0,
            new_trace=trace,
        )
        st.session_state.identity_store.save(st.session_state.identity)

        # Begin next frame
        st.session_state.frame_store.begin()

# ============================================================
# Display — Closed Frames
# ============================================================

st.divider()
st.subheader("Closed Frames")

if st.session_state.closed_frames:
    for f in st.session_state.closed_frames[-5:]:
        st.code(
            f"Frame {f.id} | fragments={len(f.fragments)}",
            language="text",
        )
else:
    st.caption("No frames closed yet.")

# ============================================================
# Display — Structural Memory
# ============================================================

st.divider()
st.subheader("Structural Memory")

traces = st.session_state.phase2.memory.traces()
if traces:
    for t in traces:
        st.code(
            f"{t.signature} | strength={t.strength:.2f} | frames={t.frames_observed}",
            language="text",
        )
else:
    st.caption("No crystallized memory yet.")

# ============================================================
# Display — Identity
# ============================================================

st.divider()
st.subheader("Identity (Continuity)")

st.json(st.session_state.identity.to_dict())
