import streamlit as st
from sandys_law_a7do.life_cycle import LifeCycle

# ==================================================
# PAGE CONFIG
# ==================================================

st.set_page_config(layout="wide")
st.title("A7DO — Development, World & Proto-Cognition Monitor")

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

snap = lc.engine.snapshot()

# ==================================================
# LIFECYCLE STATUS
# ==================================================

st.header("🧬 Lifecycle Status")
st.json({
    "Ticks": snap["ticks"],
    "Born": snap["birth"]["born"] if snap["birth"] else False,
    "Birth Reason": snap["birth"]["reason"] if snap["birth"] else None,
})

# ==================================================
# DEVELOPMENT DASHBOARD
# ==================================================

st.header("🧫 Development Dashboard")
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
# WORLD VIEW (POST-BIRTH)
# ==================================================

st.header("🗺 World")

world = snap.get("world")

if world:
    agent = world["agent"]
    width = world["cfg"]["width"]
    height = world["cfg"]["height"]

    # --- Grid ---
    grid = []
    for y in range(height):
        row = []
        for x in range(width):
            if (x, y) == (agent["x"], agent["y"]):
                row.append("🧠")
            else:
                row.append("⬜")
        grid.append(row)

    st.table(grid)

    # --- Physical state ---
    st.subheader("🧍 Physical State")
    st.json({
        "Position": (agent["x"], agent["y"]),
        "Effort": round(agent["effort"], 3),
        "Contact": agent["contact"],
        "Thermal": round(agent["thermal"], 3),
        "Pain": round(agent["pain"], 3),
    })

else:
    st.info("World not yet instantiated (pre-birth)")

# ==================================================
# SENSORY READINESS
# ==================================================

st.header("👁 Sensory Readiness")
st.json(snap["sensory"])

# ==================================================
# RAW SENSORY PACKETS (OBSERVER ONLY)
# ==================================================

st.header("🌫 Sensory Packets (Pre-Semantic)")

packets = lc.engine.state.get("last_sensory_packets", [])
if packets:
    for p in packets:
        st.markdown(
            f"- **{p.modality}** via *{p.body_region}* | "
            f"Intensity `{p.intensity}` | "
            f"Coherence `{p.coherence}` | "
            f"Repetition `{p.repetition}`"
        )
else:
    st.info("No sensory packets emitted yet")

# ==================================================
# ANATOMY
# ==================================================

st.header("🦴 Anatomy")

for region, data in snap["anatomy"].items():
    st.markdown(
        f"**{region.replace('_',' ').title()}** — "
        f"Growth `{data['growth']}` | Stability `{data['stability']}`"
    )

# ==================================================
# SQUARE (REPETITION)
# ==================================================

st.header("◼ Square (Repetition)")
if snap["square"]:
    st.json(snap["square"])
else:
    st.info("No stable repetitions yet")

# ==================================================
# BODY SCHEMA (SCUTTLING)
# ==================================================

st.header("🧠 Body Schema (Scuttling)")
st.json(snap["scuttling_candidates"])