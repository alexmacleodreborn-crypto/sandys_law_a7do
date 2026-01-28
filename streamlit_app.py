import streamlit as st
from life_cycle import LifeCycle

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(layout="wide")
st.title("A7DO — Development, Brain & World Monitor")

# ==================================================
# LIFECYCLE
# ==================================================
if "lc" not in st.session_state:
    st.session_state.lc = LifeCycle()

lc = st.session_state.lc

# ==================================================
# CONTROLS
# ==================================================
col1, col2 = st.columns(2)

with col1:
    if st.button("Tick"):
        lc.tick()

with col2:
    if st.button("Run 10 Ticks"):
        for _ in range(10):
            lc.tick()

# ==================================================
# SNAPSHOT
# ==================================================
snap = lc.engine.snapshot()
state = lc.engine.state  # internal read-only for graphs only

# ==================================================
# LIFECYCLE STATUS
# ==================================================
st.header("Lifecycle Status")

st.json({
    "Ticks": snap["ticks"],
    "Born": snap["birth"]["born"] if snap.get("birth") else False,
    "Birth Reason": snap["birth"]["reason"] if snap.get("birth") else None,
})

# ==================================================
# DEVELOPMENT DASHBOARD (BRAIN + BODY)
# ==================================================
st.header("🧠 Development & Brain Growth")

trace = state.get("development_trace", {})

if trace and len(trace.get("ticks", [])) > 2:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Womb Physiology")
        st.line_chart({
            "Heartbeat": trace["heartbeat"],
            "Stability": trace["stability"],
            "Ambient Load": trace["ambient_load"],
        })

    with col_b:
        st.subheader("Brain & Body Formation")
        st.line_chart({
            "Brain Coherence": trace["brain_coherence"],
            "Body Growth": trace["body_growth"],
            "Limb Growth": trace["limb_growth"],
        })
else:
    st.info("Development data accumulating…")

# ==================================================
# ANATOMY
# ==================================================
st.header("🦴 Anatomy (Biological Growth)")

anatomy = snap.get("anatomy", {})

if anatomy:
    for region, data in anatomy.items():
        st.markdown(
            f"**{region.replace('_', ' ').title()}**  \n"
            f"• Growth: `{data['growth']}`  \n"
            f"• Stability: `{data['stability']}`"
        )
else:
    st.info("Anatomy not yet formed")

# ==================================================
# DEVELOPMENT SILHOUETTE
# ==================================================
st.header("👶 Development Silhouette")

if anatomy:
    def pct(x): 
        return f"{int(x * 100)}%"

    st.code(
        f"""
              👶
             ┌─────┐
             │ 🧠  │  Head: {pct(anatomy['head']['growth'])}
             └──┬──┘
                │     Spine: {pct(anatomy['spine']['growth'])}
             ┌──┴──┐
             │ 🫀  │  Torso: {pct(anatomy['torso']['growth'])}
             └─┬──┬┘
        🦾 Arm: {pct(anatomy['left_arm']['growth'])}   🦾 Arm: {pct(anatomy['right_arm']['growth'])}
        🦵 Leg: {pct(anatomy['left_leg']['growth'])}   🦵 Leg: {pct(anatomy['right_leg']['growth'])}
        """,
        language="text",
    )
else:
    st.info("Silhouette unavailable")

# ==================================================
# SENSORY READINESS
# ==================================================
st.header("👁 Sensory Readiness")

st.json(snap.get("sensory", {}))

# ==================================================
# WORLD VIEW (SAFE)
# ==================================================
st.header("🌍 World")

world = snap.get("world")

if world:
    st.json(world)
else:
    st.info("World not yet connected")

# ==================================================
# SCUTTLING / BODY SCHEMA
# ==================================================
st.header("🧠 Body Schema (Scuttling)")

st.json(snap.get("scuttling_candidates", []))