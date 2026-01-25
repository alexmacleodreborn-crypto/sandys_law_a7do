import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_fragment,
    close_frame,
)
from sandys_law_a7do.engine.tick_engine import step_tick


def render_dashboard(state, snapshot):
    data = snapshot()
    metrics = data["metrics"]

    # ---------------------------------
    # STATE INIT
    # ---------------------------------
    state.setdefault("history", {"ticks": [], "Z": [], "Coherence": [], "Stability": []})
    state.setdefault("last_recorded_tick", None)

    # ---------------------------------
    # HEADER
    # ---------------------------------
    st.title("A7DO — Prebirth / Structural Dashboard")

    # ---------------------------------
    # CONTROLS
    # ---------------------------------
    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)

    if c2.button("➕ Add Phase"):
        add_fragment(state, kind="growth_phase")

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # ---------------------------------
    # SYSTEM OVERVIEW
    # ---------------------------------
    st.subheader("System Overview")
    st.json({
        "ticks": data["ticks"],
        "active_frame": data["active_frame"],
        "memory_count": data["memory_count"],
        "born": data["birth"]["born"] if data["birth"] else False,
    })

    # ---------------------------------
    # METRICS
    # ---------------------------------
    st.subheader("Structural Metrics")
    cols = st.columns(4)
    cols[0].metric("Z", metrics["Z"])
    cols[1].metric("Coherence", metrics["Coherence"])
    cols[2].metric("Stability", metrics["Stability"])
    cols[3].metric("Load", metrics["Load"])

    # ---------------------------------
    # HISTORY
    # ---------------------------------
    if state["last_recorded_tick"] != data["ticks"]:
        state["history"]["ticks"].append(data["ticks"])
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["last_recorded_tick"] = data["ticks"]

    st.subheader("Metric Evolution")
    fig, ax = plt.subplots()
    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability")
    ax.legend()
    st.pyplot(fig)

    # ---------------------------------
    # WOMB
    # ---------------------------------
    st.subheader("Prebirth — Womb State")
    if data["womb"]:
        st.table([{"metric": k, "value": v} for k, v in data["womb"].items()])
    else:
        st.caption("Womb inactive.")

    # ---------------------------------
    # BIRTH
    # ---------------------------------
    st.subheader("Birth Evaluation")
    if data["birth"]:
        st.json(data["birth"])
    else:
        st.caption("Birth not evaluated yet.")

    # ---------------------------------
    # EMBODIMENT (INERT)
    # ---------------------------------
    st.subheader("Embodiment Ledger (Read-only)")
    st.table([{"metric": k, "value": v} for k, v in data["embodiment"].items()])

    # ---------------------------------
    # FINAL SNAPSHOT
    # ---------------------------------
    st.subheader("Final Snapshot")
    st.json(data)