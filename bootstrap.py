# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (IMPORT-SAFE, LOCKED)

Responsibilities:
- Construct system state
- Wire engines together
- Provide read-only snapshot
"""

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.perception import summarize_perception

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory


# =====================================================
# SYSTEM BUILD (ONLY PLACE ENGINES ARE CREATED)
# =====================================================

def build_system():
    # ---- core containers ----
    frames = FrameStore()
    memory = StructuralMemory()

    # ---- lazy imports (CRITICAL) ----
    from sandys_law_a7do.mind.preference import (
        PreferenceEngine,
        PreferenceStore,
        PreferenceConfig,
    )

    from sandys_law_a7do.gates.engine import GateEngine

    # ---- engines ----
    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(
        store=pref_store,
        cfg=PreferenceConfig(),
    )

    gate_engine = GateEngine()

    # ---- global state ----
    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # structural load
        "structural_load": 0.0,

        # preference system
        "preference_store": pref_store,
        "preference_engine": pref_engine,
        "last_preference_update": None,

        # gate system
        "gate_engine": gate_engine,
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# =====================================================
# SNAPSHOT (PURE READ-ONLY)
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

    # ---- gate snapshot (SAFE) ----
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

        "gates": gate_view,

        "preference_top": [
            {"context": k, "score": v}
            for (k, v) in state["preference_store"].top(10)
        ],
        "last_preference_update": state.get("last_preference_update"),
    }


# =====================================================
# FRAME ACTIONS (NO ENGINE CREATION HERE)
# =====================================================

def open_frame(state: dict):
    if state["frames"].active:
        return
    state["frames"].open(Frame(domain="demo", label="ui"))


def add_fragment(state: dict):
    from sandys_law_a7do.integration.perception_loop import perceive_and_act

    frame = state["frames"].active
    if not frame:
        return

    for frag in perceive_and_act(state):
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
    frame = state["frames"].active
    if not frame:
        return

    memory: StructuralMemory = state["memory"]
    gate_engine = state["gate_engine"]
    pref_engine = state["preference_engine"]

    fragments = [{"action": f.kind} for f in frame.fragments]
    percept = summarize_perception(fragments)

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

    # ---- memory ----
    memory.add_trace(
        MemoryTrace(
            state["ticks"],
            Z,
            coherence,
            stability,
            f"{frame.domain}:{frame.label}",
            1.0,
            ["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
        )
    )

    # ---- gate evaluation ----
    gate_engine.evaluate(
        coherence=coherence,
        fragmentation=Z,
        load=load,
    )

    # ---- pressure release ----
    state["structural_load"] *= 0.6

    state["frames"].close()


def tick_system(state: dict):
    state["ticks"] += 1

    if state["frames"].active:
        state["structural_load"] = min(1.0, state["structural_load"] + 0.05)
    else:
        state["structural_load"] *= 0.6