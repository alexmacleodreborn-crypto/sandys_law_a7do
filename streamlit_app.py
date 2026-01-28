import streamlit as st
from life_cycle import LifeCycle

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("A7DO — Development & Embodiment Monitor")

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
# Snapshot
# --------------------------------------------------
snap = lc.engine.snapshot()

# ==================================================
# LIFECYCLE STATUS
# ==================================================
st.header("Lifecycle Status")
st.json({
    "Ticks": snap["ticks"],
    "Born": snap["birth"]["born"] if snap["birth"] else False,
    "Birth Reason": snap["birth"]["reason"] if snap["birth"] else None,
})

# ==================================================
# VITAL SYSTEMS
# ==================================================
st.header("Vital Systems")

st.subheader("Womb")
if snap["womb"]:
    st.json(snap["womb"])
else:
    st.info("Womb inactive")

st.subheader("Umbilical Link")
if snap["umbilical"]:
    st.json(snap["umbilical"])
else:
    st.info("Umbilical detached")

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================
st.header("🧬 Development Dashboard")

trace = lc.engine.state["development_trace"]

if len(trace["ticks"]) > 1:
    st.subheader("Cardio-Rhythmic Development")
    st.line_chart({
        "Heartbeat": trace["heartbeat"],
        "Stability": trace["stability"],
        "Ambient Load": trace["ambient_load"],
    })

    st.subheader("Growth Curves")
    st.line_chart({
        "Body Growth": trace["body_growth"],
        "Limb Growth": trace["limb_growth"],
        "Brain Coherence": trace["brain_coherence"],
    })
else:
    st.info("Development data accumulating...")

# ==================================================
# SENSORY READINESS
# ==================================================
st.header("👁 Sensory Readiness")
st.json(snap["sensory"])

# ==================================================
# ANATOMY (BIOLOGICAL BODY)
# ==================================================
st.header("🦴 Anatomy (Biological Structure)")

for region, data in snap["anatomy"].items():
    st.markdown(