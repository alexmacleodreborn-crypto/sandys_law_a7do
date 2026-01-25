# ============================================================
# A7DO SYSTEM DASHBOARD (READ-ONLY UI)
#
# Doctrine:
# - No cognition
# - No decisions
# - No learning
# - No mutation except via explicit controls
#
# This dashboard is an OBSERVER.
# ============================================================

import streamlit as st
import matplotlib.pyplot as plt

from sandys_law_a7do.bootstrap import (
    open_frame,
    add_fragment,
    close_frame,
)
from sandys_law_a7do.engine.tick_engine import step_tick
from sandys_law_a7do.interfaces.chat.observer import render_chat_observer


# ============================================================
# MAIN RENDER
# ============================================================

def render_dashboard(state: dict, snapshot) -> None:
    # --------------------------------------------------------
    # SNAPSHOT (AUTHORITATIVE READ)
    # --------------------------------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # --------------------------------------------------------
    # INIT HISTORY (ONCE)
    # --------------------------------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
            "Load": [],
        }

    if "last_recorded_tick" not in state:
        state["last_recorded_tick"] = None

    # --------------------------------------------------------
    # HEADER
    # --------------------------------------------------------
    st.title("A7DO — Sandy’s Law System Observer")

    # ========================================================
    # CONTROLS (STRUCTURAL ONLY)
    # ========================================================
    st.subheader("Structural Controls")

    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 Open Frame"):
        open_frame(state)

    if c2.button("➕ Add Phase Signal"):
        # Phase signals are still fragments structurally
        add_fragment(state, kind="phase_signal")

    if c3.button("⏹ Close Frame"):
        close_frame(state)

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)

    # --------------------------------------------------------
    # SNAPSHOT AFTER CONTROLS
    # --------------------------------------------------------
    data = snapshot()
    metrics = data["metrics"]

    # ========================================================
    # SYSTEM OVERVIEW
    # ========================================================
    st.subheader("System Overview")

    st.json(
        {
            "ticks": data["ticks"],
            "active_frame": (
                f"{data['active_frame'].domain}:{data['active_frame'].label}"
                if data["active_frame"]
                else "none"
            ),
            "memory_count": data["memory_count"],
            "born": data.get("birth", {}).get("born") if data.get("birth") else False,
        }
    )

    # ========================================================
    # STRUCTURAL METRICS
    # ========================================================
    st.subheader("Structural Metrics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Fragmentation (Z)", round(metrics["Z"], 3))
    m2.metric("Coherence", round(metrics["Coherence"], 3))
    m3.metric("Stability", round(metrics["Stability"], 3))
    m4.metric("Load", round(metrics["Load"], 3))

    # --------------------------------------------------------
    # RECORD HISTORY (MONOTONIC)
    # --------------------------------------------------------
    tick = data["ticks"]
    if state["last_recorded_tick"] != tick:
        state["history"]["ticks"].append(tick)
        state["history"]["Z"].append(metrics["Z"])
        state["history"]["Coherence"].append(metrics["Coherence"])
        state["history"]["Stability"].append(metrics["Stability"])
        state["history"]["Load"].append(metrics["Load"])
        state["last_recorded_tick"] = tick

    # ========================================================
    # METRIC EVOLUTION
    # ========================================================
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z", color="red")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence", color="blue")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability", color="green")
    ax.plot(state["history"]["ticks"], state["history"]["Load"], label="Load", color="orange")

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.set_ylim(0.0, 1.05)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # ========================================================
    # GATES (READ-ONLY)
    # ========================================================
    st.subheader("Gates")

    gates = data.get("gates", {})

    if gates:
        st.table([
            {
                "gate": name,
                "state": info.get("state"),
                "open": info.get("open"),
                "reason": info.get("reason"),
                "last_tick": info.get("last_tick"),
            }
            for name, info in gates.items()
        ])
    else:
        st.caption("No gate data available.")

    # ========================================================
    # EMBODIMENT (READ-ONLY)
    # ========================================================
    st.subheader("Embodiment Ledger Summary")

    embodiment = data.get("embodiment")

    if embodiment:
        st.table([
            {"metric": k, "value": v}
            for k, v in embodiment.items()
        ])
    else:
        st.caption("No embodied invariants consolidated.")

    # ========================================================
    # PREBIRTH / WOMB
    # ========================================================
    st.subheader("Prebirth — Womb State")

    womb = data.get("womb")

    if womb:
        st.table([
            {"metric": k, "value": v}
            for k, v in womb.items()
        ])
    else:
        st.caption("Womb inactive or birth completed.")

    # ========================================================
    # BIRTH STATE
    # ========================================================
    st.subheader("Birth Evaluation")

    birth = data.get("birth")

    if birth:
        st.json(birth)
    else:
        st.caption("Birth not yet evaluated.")

    # ========================================================
    # MEMORY (STRUCTURAL TRACE)
    # ========================================================
    st.subheader("Memory Timeline (Recent)")

    memory = state.get("memory")

    if memory and hasattr(memory, "traces") and memory.traces:
        recent = memory.traces[-10:]
        st.table([
            {
                "tick": t.tick,
                "Z": round(t.Z, 3),
                "coherence": round(t.coherence, 3),
                "stability": round(t.stability, 3),
                "frame": t.frame_signature,
                "tags": ", ".join(t.tags),
            }
            for t in recent
        ])
    else:
        st.caption("No memory traces recorded.")

    # ========================================================
    # OBSERVER CONSOLE (LANGUAGE SURFACE)
    # ========================================================
    st.subheader("Observer Console")

    observer_text = render_chat_observer(snapshot)

    st.text_area(
        label="A7DO Observer Output",
        value=observer_text,
        height=240,
    )

    # ========================================================
    # FINAL SNAPSHOT
    # ========================================================
    st.subheader("Final System Snapshot")
    st.json(data)