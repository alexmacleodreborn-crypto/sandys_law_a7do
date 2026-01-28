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
# ==================================================
# BODY MAP (STRUCTURAL EMBODIMENT)
# ==================================================

st.header("🦴 Body Map")

candidates = snap.get("scuttling_candidates", [])

# Pull ownership regions
core = None
limbs = []

for c in candidates:
    if c.get("kind") != "ownership":
        continue

    regions = c.get("regions", [])
    if "core" in regions:
        core = c
    if "limb" in regions:
        limbs.append(c)

# ---------- helpers ----------

def stability_colour(stability: float) -> str:
    if stability >= 0.9:
        return "🟩"
    if stability >= 0.6:
        return "🟨"
    return "🟥"

def support_bar(support: int) -> str:
    blocks = min(10, max(1, support // 50))
    return "█" * blocks

# ---------- render ----------

if core or limbs:
    col_l, col_c, col_r = st.columns([1, 1, 1])

    # LEFT LIMB
    with col_l:
        if limbs:
            limb = limbs[0]
            st.markdown("### 🦾 Limb")
            st.markdown(f"Stability: {stability_colour(limb['stability'])}")
            st.markdown(f"Support: `{support_bar(limb['support'])}`")
        else:
            st.markdown("### 🦾 Limb")
            st.markdown("_Not yet differentiated_")

    # CORE
    with col_c:
        if core:
            st.markdown("### 🧠 Core")
            st.markdown(f"Stability: {stability_colour(core['stability'])}")
            st.markdown(f"Support: `{support_bar(core['support'])}`")
        else:
            st.markdown("### 🧠 Core")
            st.markdown("_Not yet formed_")

    # RIGHT LIMB (mirror)
    with col_r:
        if len(limbs) > 1:
            limb = limbs[1]
            st.markdown("### 🦿 Limb")
            st.markdown(f"Stability: {stability_colour(limb['stability'])}")
            st.markdown(f"Support: `{support_bar(limb['support'])}`")
        elif limbs:
            st.markdown("### 🦿 Limb")
            st.markdown("_Differentiating_")
        else:
            st.markdown("### 🦿 Limb")
            st.markdown("_Not yet differentiated_")
else:
    st.info("Embodiment not yet established.")
    
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