from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# ============================================================
# Ensure repo root is on sys.path
# ============================================================

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ============================================================
# Core imports
# ============================================================

from sandys_law_a7do.frames import FrameStore
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.integration.phase2_loop import Phase2Loop
from sandys_law_a7do.identity import IdentityStore, IdentityEngine

# Preference + features (Stage A)
from sandys_law_a7do.accounting.feature_extract import (
    coherence_fragmentation,
    kind_distribution,
    embodiment_load,
    context_key_from_frame,
)
from sandys_law_a7do.accounting.preference import PreferenceStore

# ============================================================
# Streamlit setup
# ============================================================

st.set_page_config(page_title="A7DO — Frame-Based Mind", layout="wide")
st.title("A7DO — Frame-Based Cognitive System")
st.caption("No time • Frames only • Embodied cognition")

# ============================================================
# Session State Init
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

# Stage A preference store + history
if "prefs" not in st.session_state:
    st.session_state.prefs = PreferenceStore()

if "history" not in st.session_state:
    st.session_state.history = []  # list[dict] per closed frame

# ============================================================
# Controls — Frame interaction
# ============================================================

st.subheader("Frame Interaction")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬆️ Contact Top"):
        st.session_state.frame_store.add_fragment(
            Fragment(source="world", kind="contact", payload={"region": "top"})
        )

with col2:
    if st.button("🔥 Thermal Bottom"):
        st.session_state.frame_store.add_fragment(
            Fragment(source="world", kind="thermal", payload={"region": "bottom", "delta": 0.7})
        )

with col3:
    if st.button("💥 Force Left"):
        st.session_state.frame_store.add_fragment(
            Fragment(source="world", kind="force", payload={"region": "left", "force": 6.0})
        )

# ============================================================
# Close Frame
# ============================================================

if st.button("⏹️ Close Frame"):
    closed = st.session_state.frame_store.close()

    if closed:
        st.session_state.closed_frames.append(closed)

        # ---- Phase processing ----
        entry, pref, trace = st.session_state.phase2.step(frames=[closed])

        # ---- Identity update ----
        st.session_state.identity = st.session_state.identity_engine.update(
            st.session_state.identity,
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
            prediction_error=entry.prediction_error_l1,
            ownership_consistency=1.0,
            new_trace=trace,
        )
        st.session_state.identity_store.save(st.session_state.identity)

        # ---- Stage A: compute & update preference (descriptive only) ----
        frags = list(closed.fragments)
        C, Phi = coherence_fragmentation(frags)
        load = embodiment_load(frags)
        ctx = context_key_from_frame(frags)

        # Use prediction error from phase1 entry (already computed)
        eps = float(entry.prediction_error_l1)

        p_val, dU, dP = st.session_state.prefs.update(
            key=ctx,
            coherence=C,
            prediction_error=eps,
            load=load,
        )

        p_kind = kind_distribution(frags)

        st.session_state.history.append(
            {
                "frame_id": closed.id,
                "context": ctx,
                "coherence": C,
                "fragmentation": Phi,
                "prediction_error": eps,
                "load": load,
                "preference": p_val,
                "dU": dU,
                "dP": dP,
                "kinds": p_kind,
                "n_fragments": len(frags),
            }
        )

        # Begin next frame
        st.session_state.frame_store.begin()

# ============================================================
# Display — Identity
# ============================================================

st.divider()
st.subheader("Identity (Continuity)")
st.json(st.session_state.identity.to_dict())

# ============================================================
# Display — Preference Table
# ============================================================

st.divider()
st.subheader("Preference (Stage A)")

prefs_snapshot = st.session_state.prefs.snapshot()
if prefs_snapshot:
    dfp = pd.DataFrame.from_dict(prefs_snapshot, orient="index").reset_index().rename(columns={"index": "context"})
    dfp = dfp.sort_values(["value", "visits"], ascending=[False, False])
    st.dataframe(dfp, use_container_width=True)
else:
    st.caption("No preference entries yet. Close some frames first.")

# ============================================================
# Display — History charts
# ============================================================

st.divider()
st.subheader("Trends (per closed frame)")

if st.session_state.history:
    dfh = pd.DataFrame(st.session_state.history)

    # Show raw history table
    with st.expander("Show history table"):
        st.dataframe(dfh.drop(columns=["kinds"]), use_container_width=True)

    # Plot Prediction Error
    fig1 = plt.figure()
    plt.plot(dfh["prediction_error"].values)
    plt.title("Prediction Error (L1) across frames")
    plt.xlabel("Frame index")
    plt.ylabel("ε")
    st.pyplot(fig1)

    # Plot Coherence
    fig2 = plt.figure()
    plt.plot(dfh["coherence"].values)
    plt.title("Coherence across frames")
    plt.xlabel("Frame index")
    plt.ylabel("C")
    st.pyplot(fig2)

    # Plot Preference
    fig3 = plt.figure()
    plt.plot(dfh["preference"].values)
    plt.title("Preference value for visited contexts (sequence order)")
    plt.xlabel("Frame index")
    plt.ylabel("P(context)")
    st.pyplot(fig3)

else:
    st.caption("No closed frames yet. Close frames to generate trends.")

# ============================================================
# Display — Recent Frames
# ============================================================

st.divider()
st.subheader("Closed Frames (Recent)")

if st.session_state.closed_frames:
    for f in st.session_state.closed_frames[-5:]:
        st.code(f"Frame {f.id} | fragments={len(f.fragments)}", language="text")
else:
    st.caption("No frames closed yet.")
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="contact",
                payload={"region": "top"},
            )
        )

with col2:
    if st.button("🔥 Thermal Bottom"):
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="thermal",
                payload={"region": "bottom", "delta": 0.7},
            )
        )

with col3:
    if st.button("💥 Force Left"):
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

if st.button("⏹️ Close Frame"):
    closed = st.session_state.frame_store.close()

    if closed:
        st.session_state.closed_frames.append(closed)

        # ---- Phase processing ----
        entry, pref, trace = st.session_state.phase2.step(
            frames=[closed]
        )

        # ---- Identity update ----
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
# Display — Frames
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

