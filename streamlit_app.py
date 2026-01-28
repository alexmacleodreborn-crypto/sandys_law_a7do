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
# Womb State
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
        row.append("🧠" if (x, y) == (a.x, a.y) else "⬜")
    grid.append(row)

st.table(grid)

# ==================================================
# DEVELOPMENT DASHBOARD (NO ALTAIR)
# ==================================================

st.header("🧬 Development Dashboard")

trace = lc.engine.state.get("development_trace")

if trace and len(trace.get("ticks", [])) > 1:

    st.subheader("Gestation Timeline (Raw Signals)")

    st.write({
        "heartbeat (last 10)": trace["heartbeat"][-10:],
        "stability (last 10)": trace["stability"][-10:],
        "ambient_load (last 10)": trace["ambient_load"][-10:],
    })

    if snap.get("birth"):
        st.caption(f"Birth occurred at tick {snap['birth']['tick']}")

    st.subheader("Proto-Brain Coherence")

    st.write(trace["brain_coherence"][-20:])

    st.subheader("Embodiment Growth")

    st.write({
        "body_growth": trace["body_growth"][-20:],
        "limb_growth": trace["limb_growth"][-20:],
    })

    st.subheader("Current Development State")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Body Growth", round(trace["body_growth"][-1], 3))
    with c2:
        st.metric("Limb Growth", round(trace["limb_growth"][-1], 3))
    with c3:
        st.metric("Brain Coherence", round(trace["brain_coherence"][-1], 3))

else:
    st.info("Development data will appear after a few ticks.")

# ==================================================
# BODY MAP (STRUCTURAL EMBODIMENT)
# ==================================================

st.header("🦴 Body Map")

candidates = snap.get("scuttling_candidates", [])

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

def stability_colour(stability: float) -> str:
    if stability >= 0.9:
        return "🟩"
    if stability >= 0.6:
        return "🟨"
    return "🟥"

def support_bar(support: int) -> str:
    return "█" * min(10, max(1, support // 50))

if core or limbs:
    col_l, col_c, col_r = st.columns(3)

    with col_l:
        st.markdown("### 🦾 Limb")
        if limbs:
            limb = limbs[0]
            st.markdown(f"Stability: {stability_colour(limb['stability'])}")
            st.markdown(f"Support: `{support_bar(limb['support'])}`")
        else:
            st.markdown("_Not yet differentiated_")

    with col_c:
        st.markdown("### 🧠 Core")
        if core:
            st.markdown(f"Stability: {stability_colour(core['stability'])}")
            st.markdown(f"Support: `{support_bar(core['support'])}`")
        else:
            st.markdown("_Not yet formed_")

    with col_r:
        st.markdown("### 🦿 Limb")
        if len(limbs) > 1:
            limb = limbs[1]
            st.markdown(f"Stability: {stability_colour(limb['stability'])}")
            st.markdown(f"Support: `{support_bar(limb['support'])}`")
        elif limbs:
            st.markdown("_Differentiating_")
        else:
            st.markdown("_Not yet differentiated_")
else:
    st.info("Embodiment not yet established.")

# ==================================================
# SENSORY READINESS
# ==================================================

st.header("👁️ Sensory Readiness")

sr = snap.get("sensory_readiness")

if sr:
    st.json(sr)
else:
    st.info("Sensory readiness not yet initialised.")