import streamlit as st
from life_cycle import LifeCycle

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
# Status
# --------------------------------------------------

st.subheader("Lifecycle Status")
st.write({
    "Tick": st.session_state.tick,
    "Phase": str(lc.phase.current),
    "Born": lc.born,
})

# --------------------------------------------------
# Agent State
# --------------------------------------------------

a = lc.world.agent
st.subheader("Agent Body")

st.write({
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

st.subheader("World Grid")

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
