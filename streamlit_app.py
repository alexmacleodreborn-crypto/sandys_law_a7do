import streamlit as st
from life_cycle import LifeCycle

# --------------------------------------------------
# Page config
# --------------------------------------------------

st.set_page_config(layout="wide")
st.title("A7DO – Living System Viewer")

# --------------------------------------------------
# Persistent lifecycle
# --------------------------------------------------

if "lc" not in st.session_state:
    st.session_state.lc = LifeCycle()
    st.session_state.tick = 0

lc = st.session_state.lc

# --------------------------------------------------
# Controls
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("Tick"):
        lc.tick()
        st.session_state.tick += 1

with col2:
    if st.button("Run 10 Ticks"):
        for _ in range(10):
            lc.tick()
            st.session_state.tick += 1

# --------------------------------------------------
# Snapshot
# --------------------------------------------------

snap = lc.engine.snapshot()

# --------------------------------------------------
# Lifecycle Status
# --------------------------------------------------

st.header("Lifecycle Status")

st.json({
    "Ticks": snap["ticks"],
    "Born": snap["birth"]["born"] if snap.get("birth") else False,
    "Birth Reason": snap["birth"]["reason"] if snap.get("birth") else None,
})

# --------------------------------------------------
# Womb State (pre + post birth snapshot)
# --------------------------------------------------

st.header("Womb State")

if snap.get("womb"):
    st.json(snap["womb"])
else:
    st.info("Womb inactive.")

# --------------------------------------------------
# Gate States
# --------------------------------------------------

st.header("Gate States")

if snap.get("gates"):
    st.json(snap["gates"])
else:
    st.info("No gate data available.")

# --------------------------------------------------
# Scuttling Candidates
# --------------------------------------------------

st.header("Scuttling Candidates")
st.json(snap.get("scuttling_candidates", []))

# --------------------------------------------------
# Agent Body
# --------------------------------------------------

st.header("Agent Body")

a = lc.world.agent

st.json({
    "x": a.x,
    "y": a.y,
    "effort": round(a.effort, 3),
    "contact": a.contact,
    "thermal": round(a.thermal, 3),
    "pain": round(a.pain, 3),
})

# --------------------------------------------------
# World Grid
# --------------------------------------------------

st.header("World Grid")

grid = []
for y in range(lc.world.cfg.height):
    row = []
    for x in range(lc.world.cfg.width):
        if (x, y) == (a.x, a.y):
            row.append("🧠")
        else:
            row.append("⬜")
    grid.append(row)

st.table(grid)

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================

st.header("🧬 Development Dashboard")

trace = lc.engine.state.get("development_trace")

if trace and len(trace.get("ticks", [])) > 1:

    # -------------------------------
    # Gestation Timeline
    # -------------------------------
    st.subheader("Gestation Timeline")

    st.line_chart({
        "Heartbeat": trace["heartbeat"],
        "Rhythmic Stability": trace["stability"],
        "Ambient Load": trace["ambient_load"],
    })

    if snap.get("birth"):
        st.caption(f"Birth occurred at tick {snap['birth']['tick']}")

    # -------------------------------
    # Proto-Brain Development
    # -------------------------------
    st.subheader("Proto-Brain Coherence (Pre-Cognitive)")

    st.area_chart({
        "Coherence Capacity": trace["brain_coherence"],
    })

    # -------------------------------
    # Embodiment Growth
    # -------------------------------
    st.subheader("Embodiment Growth")

    st.line_chart({
        "Body Growth": trace["body_growth"],
        "Limb Differentiation": trace["limb_growth"],
    })

    # -------------------------------
    # Current Development Metrics
    # -------------------------------
    st.subheader("Current Development State")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Body Growth", round(trace["body_growth"][-1], 3))

    with col2:
        st.metric("Limb Growth", round(trace["limb_growth"][-1], 3))

    with col3:
        st.metric("Brain Coherence", round(trace["brain_coherence"][-1], 3))

else:
    st.info("Development data will appear after a few ticks.")