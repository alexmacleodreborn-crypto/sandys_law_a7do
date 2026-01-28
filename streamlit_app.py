import streamlit as st
from sandys_law_a7do.life_cycle import LifeCycle

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(layout="wide")
st.title("A7DO — Development & Vital Systems Monitor")

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
trace = lc.engine.state.get("development_trace")

# ==================================================
# LIFECYCLE STATUS
# ==================================================
st.header("Lifecycle Status")

st.json(
    {
        "Ticks": snap["ticks"],
        "Born": snap["birth"]["born"] if snap.get("birth") else False,
        "Birth Reason": snap["birth"]["reason"] if snap.get("birth") else None,
    }
)

# ==================================================
# VITAL SYSTEMS
# ==================================================
st.header("🫀 Vital Systems")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Womb")
    if snap.get("womb"):
        st.json(snap["womb"])
    else:
        st.info("Womb inactive")

with c2:
    st.subheader("Umbilical Link")
    if snap.get("umbilical"):
        st.json(snap["umbilical"])
    else:
        st.info("Umbilical detached")

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================
st.header("🧬 Development Dashboard")

if trace and len(trace["ticks"]) > 1:
    st.subheader("🫀 Cardio-Rhythmic Development")
    st.write(
        {
            "heartbeat (last 10)": trace["heartbeat"][-10:],
            "rhythmic coupling (last 10)": trace["rhythmic_coupling"][-10:],
        }
    )

    st.subheader("🧠 Neural Coherence Formation")
    st.write(trace["brain_coherence"][-20:])

    st.subheader("🦴 Somatic Development")
    st.write(
        {
            "body_growth": trace["body_growth"][-20:],
            "limb_growth": trace["limb_growth"][-20:],
        }
    )

    st.subheader("Current Development State")
    m1, m2, m3 = st.columns(3)
    with m1:
        st.metric("Body Growth", round(trace["body_growth"][-1], 3))
    with m2:
        st.metric("Limb Growth", round(trace["limb_growth"][-1], 3))
    with m3:
        st.metric("Brain Coherence", round(trace["brain_coherence"][-1], 3))
else:
    st.info("Development data will appear after a few ticks.")

# ==================================================
# SENSORY READINESS
# ==================================================
st.header("👁️ Sensory Readiness")

if snap.get("sensory"):
    st.json(snap["sensory"])
else:
    st.info("Sensory systems offline.")

# ==================================================
# BODY MAP
# ==================================================
st.header("🦴 Body Map")

candidates = snap.get("scuttling_candidates", [])
core = None
limbs = []

for c in candidates:
    if c.get("kind") != "ownership":
        continue
    if "core" in c.get("regions", []):
        core = c
    if "limb" in c.get("regions", []):
        limbs.append(c)


def stability_colour(v: float) -> str:
    if v >= 0.9:
        return "🟩"
    if v >= 0.6:
        return "🟨"
    return "🟥"


def support_bar(s: int) -> str:
    return "█" * min(10, max(1, s // 50))


if core or limbs:
    l, c, r = st.columns(3)

    with l:
        st.markdown("### 🦾 Limb")
        if limbs:
            st.markdown(
                f"Stability: {stability_colour(limbs[0]['stability'])}"
            )
            st.markdown(
                f"Support: `{support_bar(limbs[0]['support'])}`"
            )
        else:
            st.markdown("_Not yet differentiated_")

    with c:
        st.markdown("### 🧠 Core")
        if core:
            st.markdown(
                f"Stability: {stability_colour(core['stability'])}"
            )
            st.markdown(
                f"Support: `{support_bar(core['support'])}`"
            )
        else:
            st.markdown("_Not yet formed_")

    with r:
        st.markdown("### 🦿 Limb")
        if len(limbs) > 1:
            st.markdown(
                f"Stability: {stability_colour(limbs[1]['stability'])}"
            )
            st.markdown(
                f"Support: `{support_bar(limbs[1]['support'])}`"
            )
        elif limbs:
            st.markdown("_Differentiating_")
        else:
            st.markdown("_Not yet differentiated_")
else:
    st.info("Embodiment not yet established.")