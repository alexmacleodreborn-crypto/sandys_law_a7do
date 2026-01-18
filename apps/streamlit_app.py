from __future__ import annotations

import streamlit as st
from typing import List

# ------------------------------------------------------------
# World (Phase 0)
# ------------------------------------------------------------

from world.world_state import make_default_world, WorldEvent
from world.actuators import ActuatorSuite, ActionIntent
from world.sensors import SensorSuite

# ------------------------------------------------------------
# Phase 1 Integration
# ------------------------------------------------------------

from integration.phase1_loop import Phase1Loop


# ============================================================
# Streamlit App Setup
# ============================================================

st.set_page_config(
    page_title="A7DO — Frame-Based World",
    layout="wide",
)

st.title("A7DO — Frame-Based World (Phase 0 → Phase 1)")
st.caption("No time • No reward • Frames only • Structural coherence")

# ============================================================
# Session State Initialization
# ============================================================

if "world" not in st.session_state:
    st.session_state.world = make_default_world()

if "actuators" not in st.session_state:
    st.session_state.actuators = ActuatorSuite(st.session_state.world)

if "sensors" not in st.session_state:
    st.session_state.sensors = SensorSuite(st.session_state.world)

if "phase1" not in st.session_state:
    st.session_state.phase1 = Phase1Loop()

if "frames" not in st.session_state:
    st.session_state.frames: List[List[WorldEvent]] = []

if "last_events" not in st.session_state:
    st.session_state.last_events: List[WorldEvent] = []


# ============================================================
# Helper: Advance One Frame
# ============================================================

def run_frame(intent: ActionIntent | None) -> None:
    """
    Execute exactly ONE frame:
    Action → Physics → Sensors → Events
    """
    frame_events: List[WorldEvent] = []

    # Apply action if provided
    if intent is not None:
        frame_events.extend(
            st.session_state.actuators.apply(intent)
        )

    # Always sense after physics
    frame_events.extend(
        st.session_state.sensors.sense()
    )

    # Store
    st.session_state.last_events = frame_events
    st.session_state.frames.append(frame_events)

    # Limit frame history (frames ≠ time)
    MAX_FRAMES = 6
    st.session_state.frames = st.session_state.frames[-MAX_FRAMES:]


# ============================================================
# Controls
# ============================================================

st.subheader("Controls")

col_move, col_info = st.columns([1, 3])

with col_move:
    if st.button("⬆️ Up"):
        run_frame(ActionIntent(name="move", payload={"dx": 0, "dy": -1}))

    if st.button("⬇️ Down"):
        run_frame(ActionIntent(name="move", payload={"dx": 0, "dy": 1}))

    if st.button("⬅️ Left"):
        run_frame(ActionIntent(name="move", payload={"dx": -1, "dy": 0}))

    if st.button("➡️ Right"):
        run_frame(ActionIntent(name="move", payload={"dx": 1, "dy": 0}))

    if st.button("No Action (Sense Only)"):
        run_frame(None)

with col_info:
    st.markdown(
        """
        **Frame Doctrine**
        - Each button press = **one frame**
        - No clocks, no loops, no background ticking
        - Learning comes from structure, not reward
        """
    )

# ============================================================
# World Snapshot
# ============================================================

st.subheader("World Snapshot")

ws = st.session_state.world.snapshot()

col_w1, col_w2 = st.columns(2)

with col_w1:
    st.json(ws["agent"])

with col_w2:
    st.json({
        "walls_count": ws["walls_count"],
        "event_counter": ws["event_counter"],
    })

# ============================================================
# Last Frame Events
# ============================================================

st.subheader("Last Frame Events")

if st.session_state.last_events:
    for e in st.session_state.last_events:
        st.code(
            f"{e.type.value.upper():>11} | {e.name:<20} | {e.payload}",
            language="text",
        )
else:
    st.caption("No frames yet.")

# ============================================================
# Phase 1 Analysis (Prediction → Accounting → Preference)
# ============================================================

if st.session_state.frames:
    entry, pref = st.session_state.phase1.step(
        frames=st.session_state.frames
    )

    st.subheader("Phase 1 — Structural Signals")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric("Coherence", f"{entry.coherence:.2f}")
        st.metric("Fragmentation", f"{entry.fragmentation:.2f}")

    with c2:
        st.metric("Prediction Error", f"{entry.prediction_error_l1:.2f}")
        st.metric("Block Rate", f"{entry.outcome_block_rate:.2f}")

    with c3:
        st.metric("Context Preference", f"{pref.updated:.2f}")
        st.caption(f"Context: {pref.context_key}")
        st.caption(f"Δ Preference: {pref.delta:+.3f}")

    if entry.notes:
        st.caption("Notes: " + ", ".join(entry.notes))

else:
    st.caption("Phase 1 will activate after the first frame.")

# ============================================================
# Footer
# ============================================================

st.divider()
st.caption(
    "A7DO • Sandy’s Law • Frames ≠ Time • Stability before Intelligence"
)
