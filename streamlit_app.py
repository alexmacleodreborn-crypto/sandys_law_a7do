import streamlit as st
from life_cycle import LifeCycle

st.set_page_config(layout="wide")
st.title("A7DO — Development, Body & Proto-Cognition")

if "lc" not in st.session_state:
    st.session_state.lc = LifeCycle()

lc = st.session_state.lc

col1, col2 = st.columns(2)
with col1:
    if st.button("Tick"):
        lc.tick()
with col2:
    if st.button("Run 10 Ticks"):
        for _ in range(10):
            lc.tick()

snap = lc.engine.snapshot()

# ==================================================
# LIFECYCLE
# ==================================================
st.header("Lifecycle Status")
st.json({
    "Ticks": snap["ticks"],
    "Born": snap["birth"]["born"] if snap["birth"] else False,
    "Birth Reason": snap["birth"]["reason"] if snap["birth"] else None,
})

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================
st.header("🧬 Development Dashboard")
trace = lc.engine.state["development_trace"]

if len(trace["ticks"]) > 2:
    st.line_chart({
        "Heartbeat": trace["heartbeat"],
        "Stability": trace["stability"],
        "Body Growth": trace["body_growth"],
        "Brain Coherence": trace["brain_coherence"],
    })
else:
    st.info("Development data accumulating…")

# ==================================================
# SENSORY
# ==================================================
st.header("👁 Sensory Readiness")
st.json(snap["sensory"])

# ==================================================
# BODY
# ==================================================
st.header("🦴 Anatomy")
for region, data in snap["anatomy"].items():
    st.markdown(
        f"**{region.replace('_',' ').title()}** — "
        f"Growth `{data['growth']}` | Stability `{data['stability']}`"
    )

# ==================================================
# SQUARE
# ==================================================
st.header("◼ Square (Repetition)")
st.json(snap["square"])

# ==================================================
# SCUTTLING
# ==================================================
st.header("🧠 Body Schema (Scuttling)")
st.json(snap["scuttling_candidates"])