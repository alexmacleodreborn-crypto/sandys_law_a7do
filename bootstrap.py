# =====================================================
# SNAPSHOT (READ-ONLY)
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine = state.get("gate_engine")

    active = frames.active

    if active:
        fragments = [{"action": f.kind} for f in active.fragments]
        percept = summarize_perception(fragments)
    else:
        percept = summarize_perception([])

    report = compute_coherence(
        fragment_count=percept.fragment_count,
        unique_actions=percept.unique_actions,
        blocked_events=0,
        percept_notes=percept.notes,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    regulation = regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=report.block_rate,
    )

    # -------------------------------
    # GATE SNAPSHOT (SAFE)
    # -------------------------------
    gate_view = {}

    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            gate_view[name] = {
                "score": gs.result.score,
                "decision": gs.result.decision.value,
                "reason": gs.result.reason,
                "last_tick": gs.last_tick,
            }

    # -------------------------------
    # RETURN
    # -------------------------------
    return {
        "ticks": state["ticks"],
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
        },
        "regulation": regulation,
        "active_frame": active,
        "memory_count": memory.count(),

        # Gates (read-only structural control)
        "gates": gate_view,

        # Preferences (read-only bias)
        "preference_top": [
            {"context": k, "score": v}
            for (k, v) in state["preference_store"].top(10)
        ],
        "last_preference_update": state.get("last_preference_update"),
    }