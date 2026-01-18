from __future__ import annotations

import streamlit as st
import pandas as pd

# ============================================================
# Core imports
# ============================================================

from frames import FrameStore
from frames.fragment import Fragment

from embodiment.boundaries import BoundaryMap, Boundary
from embodiment.ownership import OwnershipResolver
from embodiment.ledger import EmbodimentLedger
from embodiment.thermal_pain import ThermalPainProcessor

from integration.embodiment_observer import EmbodimentObserver
from integration.phase2_loop import Phase2Loop

from identity import IdentityStore, IdentityEngine


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

if "frames_closed" not in st.session_state:
    st.session_state.frames_closed = []

# ---------------- Embodiment ----------------

if "boundaries" not in st.session_state:
    bm = BoundaryMap()
    bm.add(Boundary("left", (0, 0), (0, 4)))
    bm.add(Boundary("right", (4, 0), (4, 4)))
    bm.add(Boundary("top", (0, 0), (4, 0)))
    bm.add(Boundary("bottom", (0, 4), (4, 4)))
    st.session_state.boundaries = bm

if "ledger" not in st.session_state:
    st.session_state.ledger = EmbodimentLedger()

if "ownership" not in st.session_state:
    st.session_state.ownership = OwnershipResolver(
        known_regions={"left", "right", "top", "bottom"}
    )

if "thermal" not in st.session_state:
    st.session_state.thermal = ThermalPainProcessor()

if "embodiment_observer" not in st.session_state:
    st.session_state.embodiment_observer = EmbodimentObserver(
        boundaries=st.session_state.boundaries,
        ownership=st.session_state.ownership,
        ledger=st.session_state.ledger,
        thermal=st.session_state.thermal,
    )

# ---------------- Phase Loops ----------------

if "phase2" not in st.session_state:
    st.session_state.phase2 = Phase2Loop()

# ---------------- Identity ----------------

if "identity_store" not in st.session_state:
    st.session_state.identity_store = IdentityStore("data/identity/identity.json")
    st.session_state.identity_engine = IdentityEngine()
    st.session_state.identity = st.session_state.identity_store.load()

# ============================================================
# Controls
# ============================================================

st.subheader("World Interaction (Frame-Based)")

col1, col2, col3 = st.columns(3)

with col1:
    if st.button("⬆️ Contact Top"):
        st.session_state.frame_store.add_fragment(
            Fragment(
                source="world",
                kind="contact",
                payload={"x": 2, "y": 0},
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

if st.button("⏹️ Close Frame"):
    closed = st.session_state.frame_store.close()
    if closed:
        st.session_state.frames_closed.append(closed)
        st.session_state.embodiment_observer.observe_frame(closed)

        # Phase 1 + 2
        entry, pref, trace = st.session_state.phase2.step(
            frames=[[f for f in closed.fragments]]
        )

        # Identity update (ownership consistency placeholder = 0.8)
        st.session_state.identity = st.session_state.identity_engine.update(
            st.session_state.identity,
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
            prediction_error=entry.prediction_error_l1,
            ownership_consistency=0.8,
            new_trace=trace,
        )

        st.session_state.identity_store.save(st.session_state.identity)

# ============================================================
# Display
# ============================================================

st.divider()
st.subheader("Frames")

for f in st.session_state.frames_closed[-5:]:
    st.code(
        f"Frame {f.id} | fragments={len(f.fragments)}",
        language="text",
    )

# ---------------- Embodiment ----------------

st.divider()
st.subheader("Embodiment Ledger")

ledger_snapshot = st.session_state.ledger.snapshot()
if ledger_snapshot:
    df = pd.DataFrame.from_dict(
        {k: vars(v) for k, v in ledger_snapshot.items()},
        orient="index",
    )
    st.dataframe(df)
else:
    st.caption("No embodiment data yet.")

# ---------------- Memory ----------------

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

# ---------------- Identity ----------------

st.divider()
st.subheader("Identity (Continuity)")

st.json(st.session_state.identity.to_dict())