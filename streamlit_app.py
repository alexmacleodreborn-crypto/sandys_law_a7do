import streamlit as st
from life_cycle import LifeCycle

st.set_page_config(layout="wide")
st.title("A7DO – Living System Viewer")

# --------------------------------------------------
# Persistent lifecycle
# --------------------------------------------------

if "lc" not in st.session_state:
    st.session_state.lc = LifeCycle()

lc = st.session_state.lc

# --------------------------------------------------
# Controls
# --------------------------------------------------

col1, col2 = st.columns(2)

with col1:
    if st.button("Tick"):
        lc.tick()

with col2:
    if st.button("Run 10 Ticks"):
        for _ in range(10):
            lc.tick()

# --------------------------------------------------
# Authoritative snapshot
# --------------------------------------------------

snap = lc.engine.snapshot()

# --------------------------------------------------
# Lifecycle Status
# --------------------------------------------------

st.subheader("Lifecycle Status")

st.write({
    "Ticks": snap.get("ticks"),
    "Born": bool(snap.get("birth")),
    "Birth Reason": snap["birth"]["reason"] if snap.get("birth") else None,
})

# --------------------------------------------------
# Womb State (Prebirth visibility)
# --------------------------------------------------

if snap.get("womb"):
    st.subheader("Womb State")
    st.write(snap["womb"])

# --------------------------------------------------
# Gate State
# --------------------------------------------------

if snap.get("gates"):
    st.subheader("Gate States")
    st.write(snap["gates"])

# --------------------------------------------------
# Scuttling (Candidates)
# --------------------------------------------------

if snap.get("scuttling_candidates"):
    st.subheader("Scuttling Candidates")
    st.write(snap["scuttling_candidates"])

# --------------------------------------------------
# World View (Phase-0 Physical World)
# --------------------------------------------------

st.subheader("World Grid")

world = lc.world
agent = world.agent

grid = []
for y in range(world.cfg.height):
    row = []
    for x in range(world.cfg.width):
        if (x, y) == (agent.x, agent.y):
            row.append("🧠")
        else:
            row.append("⬜")
    grid.append(row)

st.table(grid)

# --------------------------------------------------
# Agent Body (Physical Signals Only)
# --------------------------------------------------

st.subheader("Agent Body")

st.write({
    "x": agent.x,
    "y": agent.y,
    "effort": round(agent.effort, 3),
    "contact": agent.contact,
    "thermal": round(agent.thermal, 3),
    "pain": round(agent.pain, 3),
})