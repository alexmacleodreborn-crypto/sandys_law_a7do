import streamlit as st
from life_cycle import LifeCycle

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(layout="wide")
st.title("A7DO — Development & Embodiment Monitor")

# ==================================================
# PERSISTENT LIFECYCLE
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
# VITAL SYSTEMS
# ==================================================

st.header("Vital Systems")

col_w, col_u = st.columns(2)

with col_w:
    st.subheader("🫀 Womb")
    if snap.get("womb"):
        st.json(snap["womb"])
    else:
        st.info("Womb inactive")

with col_u:
    st.subheader("🔌 Umbilical Link")
    if snap.get("umbilical"):
        st.json(snap["umbilical"])
    else:
        st.info("Umbilical detached")

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================

st.header("🧬 Development Dashboard")

trace = lc.engine.state.get("development_trace", {})

if trace and len(trace.get("ticks", [])) > 1:
    col_a, col_b = st.columns(2)

    with col_a:
        st.subheader("Cardio-Rhythmic Development")
        st.line_chart({
            "Heartbeat": trace["heartbeat"],
            "Rhythmic Stability": trace["stability"],
            "Ambient Load": trace["ambient_load"],
        })

    with col_b:
        st.subheader("Growth Curves")
        st.line_chart({
            "Body Growth": trace["body_growth"],
            "Limb Growth": trace["limb_growth"],
            "Brain Coherence": trace["brain_coherence"],
        })
else:
    st.info("Development data accumulating…")

# ==================================================
# SENSORY READINESS (POST-BIRTH RAMP)
# ==================================================

st.header("👁️ Sensory Readiness")

if snap.get("sensory"):
    st.json(snap["sensory"])
else:
    st.info("Sensory systems not yet active")

# ==================================================
# ANATOMY — BIOLOGICAL BODY
# ==================================================

st.header("🦴 Anatomy (Biological Structure)")

anatomy = snap.get("anatomy")

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
# DEVELOPMENT SILHOUETTE (OBSERVER ONLY)
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
# BODY SCHEMA (SCUTTLING)
# ==================================================

st.header("🧠 Body Schema (Scuttling)")

sc = snap.get("scuttling_candidates", [])

if sc:
    st.json(sc)
else:
    st.info("Body schema not yet stabilized")