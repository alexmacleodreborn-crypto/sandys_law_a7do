# sandys_law_a7do/interfaces/dashboard/streamlit_app.py
"""
A7DO — Sandy’s Law Dashboard
FINAL frame-safe version

Rules enforced:
- Exactly ONE active frame
- Tick is observational only
- UI enforces frame lifecycle
"""

import streamlit as st

from sandys_law_a7do.bootstrap import (
    build_system,
    inject_demo_frame,
    add_fragment_by_kind,
    close_frame,
    tick_system,
)

# --------------------------------------------------
# INIT SYSTEM (ONCE)
# --------------------------------------------------

if "a7do_state" not in st.session_state:
    _, snapshot, state = build_system()
    st.session_state.a7do_state = state
    st.session_state.snapshot_fn = snapshot

state = st.session_state.a7do_state
snapshot = st.session_state.snapshot_fn


# --------------------------------------------------
# UI
# --------------------------------------------------

st.set_page_config(
    page_title="A7DO — Sandy’s Law Dashboard",
    layout="wide",
)

st.title("A7DO — Sandy’s Law System Dashboard")

# ==================================================
# SIDEBAR CONTROLS
# ==================================================

st.sidebar.title("A7DO Control Panel")

# ------------------------------
# FRAME CONTROL
# ------------------------------

st.sidebar.markdown("### Frame Lifecycle")

if st.sidebar.button("▶ New Frame"):
    # HARD RULE: only one active frame
    if state["frames"].active is not None:
        close_frame(state)
    inject_demo_frame(state)

if st.sidebar.button("➕ Add Fragment"):
    # Ensure a frame exists
    if state["frames"].active is None:
        inject_demo_frame(state)
    add_fragment_by_kind(state, "demo")

if st.sidebar.button("⏹ Close Frame"):
    close_frame(state)

st.sidebar.divider()

# ------------------------------
# TICK (OBSERVATIONAL)
# ------------------------------

if st.sidebar.button("⏱ Tick"):
    tick_system(state)

# ==================================================
# SNAPSHOT (AFTER ALL ACTIONS)
# ==================================================

data = snapshot()

# ==================================================
# SYSTEM OVERVIEW
# ==================================================

st.subheader("System Overview")

st.json(
    {
        "ticks": data["ticks"],
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

st.subheader("Regulation Decision")
st.json(data["regulation"])

# ==================================================
# MEMORY
# ==================================================

st.subheader("Structural Memory")

st.metric(
    label="Crystallised Memory Count",
    value=data["memory_count"],
)

if data["memory_count"] > 0:
    st.success("Memory crystallised under stable conditions")
else:
    st.info("No crystallised memory yet")

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