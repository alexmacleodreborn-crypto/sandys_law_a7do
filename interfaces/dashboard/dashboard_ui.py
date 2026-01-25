from __future__ import annotations

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
# A7DO DASHBOARD (AUTHORITATIVE UI)
# ============================================================

def render_dashboard(state: dict, snapshot):
    # --------------------------------------------------
    # INITIAL SNAPSHOT
    # --------------------------------------------------
    data = snapshot()
    metrics = data.get("metrics", {})

    # --------------------------------------------------
    # INIT HISTORY (ONCE)
    # --------------------------------------------------
    if "history" not in state:
        state["history"] = {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        }

    if "record_history" not in state:
        state["record_history"] = False

    if "last_recorded_tick" not in state:
        state["last_recorded_tick"] = None

    # --------------------------------------------------
    # HEADER
    # --------------------------------------------------
    st.title("A7DO — Sandy’s Law System Dashboard")

    # --------------------------------------------------
    # CONTROLS
    # --------------------------------------------------
    st.subheader("Controls")

    c1, c2, c3, c4 = st.columns(4)

    if c1.button("🆕 New Frame"):
        open_frame(state)
        state["record_history"] = True

    if c2.button("➕ Add Phase"):
        # Phase replaces raw fragment semantics
        add_fragment(state, kind="phase", payload={})
        state["record_history"] = True

    if c3.button("⏹ Close Frame"):
        close_frame(state)
        state["record_history"] = True

    if c4.button("⏭ Tick"):
        step_tick(state, snapshot)
        state["record_history"] = True

    # --------------------------------------------------
    # SNAPSHOT AFTER CONTROLS
    # --------------------------------------------------
    data = snapshot()
    metrics = data.get("metrics", {})

    # --------------------------------------------------
    # SYSTEM OVERVIEW
    # --------------------------------------------------
    st.subheader("System Overview")

    birth = data.get("birth") or {}

    st.json(
        {
            "ticks": data.get("ticks"),
            "active_frame": (
                f"{data['active_frame'].domain}:{data['active_frame'].label}"
                if data.get("active_frame")
                else "none"
            ),
            "memory_count": data.get("memory_count"),
            "born": birth.get("born", False),
        }
    )

    # --------------------------------------------------
    # STRUCTURAL METRICS
    # --------------------------------------------------
    st.subheader("Structural Metrics")

    m1, m2, m3, m4 = st.columns(4)

    m1.metric("Z (Fragmentation)", round(metrics.get("Z", 0.0), 3))
    m2.metric("Coherence", round(metrics.get("Coherence", 0.0), 3))
    m3.metric("Stability", round(metrics.get("Stability", 0.0), 3))
    m4.metric("Load", round(metrics.get("Load", 0.0), 3))

    # --------------------------------------------------
    # RECORD HISTORY (SAFE)
    # --------------------------------------------------
    should_record = (
        data.get("active_frame") is not None
        or state["record_history"]
    )

    if should_record and state["last_recorded_tick"] != data.get("ticks"):
        state["history"]["ticks"].append(data.get("ticks"))
        state["history"]["Z"].append(metrics.get("Z", 0.0))
        state["history"]["Coherence"].append(metrics.get("Coherence", 0.0))
        state["history"]["Stability"].append(metrics.get("Stability", 0.0))

        state["last_recorded_tick"] = data.get("ticks")
        state["record_history"] = False

    # --------------------------------------------------
    # METRIC EVOLUTION GRAPH
    # --------------------------------------------------
    st.subheader("Metric Evolution")

    fig, ax = plt.subplots(figsize=(9, 4))

    ax.plot(state["history"]["ticks"], state["history"]["Z"], label="Z", color="red")
    ax.plot(state["history"]["ticks"], state["history"]["Coherence"], label="Coherence", color="blue")
    ax.plot(state["history"]["ticks"], state["history"]["Stability"], label="Stability", color="green")

    ax.set_xlabel("Tick")
    ax.set_ylabel("Value")
    ax.set_ylim(0.0, 1.05)
    ax.legend()
    ax.grid(True)

    st.pyplot(fig)

    # --------------------------------------------------
    # GATES (READ-ONLY)
    # --------------------------------------------------
    st.subheader("Gates")

    gates = data.get("gates", {})

    if gates:
        st.table(
            [
                {
                    "gate": name,
                    "state": info.get("state"),
                    "open": info.get("open"),
                    "reason": info.get("reason"),
                    "last_tick": info.get("last_tick"),
                }
                for name, info in gates.items()
            ]
        )
    else:
        st.caption("No gate data available.")

    # --------------------------------------------------
    # EMBODIMENT (READ-ONLY)
    # --------------------------------------------------
    st.subheader("Embodiment Ledger Summary")

    embodiment = data.get("embodiment")

    if embodiment:
        st.table(
            [{"metric": k, "value": v} for k, v in embodiment.items()]
        )
    else:
        st.caption("No embodied invariants consolidated yet.")

    # --------------------------------------------------
    # PREBIRTH / WOMB
    # --------------------------------------------------
    st.subheader("Prebirth — Womb State")

    womb = data.get("womb")

    if womb:
        st.table(
            [{"metric": k, "value": v} for k, v in womb.items()]
        )
    else:
        st.caption("Womb inactive or birth complete.")

    # --------------------------------------------------
    # BIRTH STATE
    # --------------------------------------------------
    st.subheader("Birth Evaluation")

    if birth:
        st.json(birth)
    else:
        st.caption("Birth not yet evaluated.")

    # --------------------------------------------------
    # MEMORY TIMELINE
    # --------------------------------------------------
    st.subheader("Memory Timeline (Recent)")

    memory = state.get("memory")

    if memory and hasattr(memory, "traces") and memory.traces:
        recent = memory.traces[-10:]
        st.table(
            [
                {
                    "tick": t.tick,
                    "Z": round(t.Z, 3),
                    "coherence": round(t.coherence, 3),
                    "stability": round(t.stability, 3),
                    "frame": t.frame_signature,
                    "tags": ", ".join(t.tags),
                }
                for t in recent
            ]
        )
    else:
        st.caption("No memory traces recorded yet.")

    # --------------------------------------------------
    # CHAT OBSERVER (READ-ONLY)
    # --------------------------------------------------
    st.subheader("Observer Console")

    observer_text = render_chat_observer(snapshot)

    st.text_area(
        label="A7DO Observer Output",
        value=observer_text,
        height=220,
    )

    # --------------------------------------------------
    # FINAL SNAPSHOT
    # --------------------------------------------------
    st.subheader("Final State Snapshot")
    st.json(data)