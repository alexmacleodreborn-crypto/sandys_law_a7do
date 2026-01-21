# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (LOCKED)

Implements:
- Frame lifecycle
- Tick counter
- OPTION A: Episode commit on frame close
- Structural metrics (Z, coherence, stability)
- Preference drift (read-only bias)
- Gate evaluation & snapshot (symbolic, non-scored)

IMPORTANT:
- Gates return DECISIONS, not numeric scores
- Snapshot reflects true GateDecision schema
"""

# =====================================================
# IMPORTS
# =====================================================

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate

from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory

from sandys_law_a7do.integration.perception_loop import perceive_and_act

from sandys_law_a7do.gates.engine import GateEngine


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(store=pref_store, cfg=PreferenceConfig())

    gate_engine = GateEngine()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # Structural load (Phase 5)
        "structural_load": 0.0,

        # Preferences (Phase 6)
        "preference_store": pref_store,
        "preference_engine": pref_engine,
        "last_preference_update": None,

        # Gates (Phase 7)
        "gate_engine": gate_engine,
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# =====================================================
# SNAPSHOT (READ-ONLY)
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames = state["frames"]
    memory = state["memory"]
    gate_engine: GateEngine = state.get("gate_engine")

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

    # ----------------------------
    # Gate snapshot (FIXED)
    # ----------------------------

    gate_view = {}

    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            gate_view[name] = {
                "state": gs.result.state,
                "reason": gs.result.reason,
                "last_tick": gs.last_tick,
            }

    # ----------------------------
    # Preference visibility
    # ----------------------------

    pref_store: PreferenceStore = state["preference_store"]
    top_contexts = pref_store.top(10)

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

        # Phase 6
        "preference_top": [
            {"context": k, "score": v} for (k, v) in top_contexts
        ],
        "last_preference_update": state.get("last_preference_update"),

        # Phase 7
        "gates": gate_view,
    }


# =====================================================
# FRAME ACTIONS
# =====================================================

def open_frame(state: dict):
    if state["frames"].active:
        return
    state["frames"].open(Frame(domain="demo", label="ui"))


def add_fragment(state: dict):
    frame = state["frames"].active
    if not frame:
        return
    for frag in perceive_and_act(state):
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
    frames = state["frames"]
    memory = state["memory"]
    gate_engine: GateEngine = state["gate_engine"]

    frame = frames.active
    if not frame:
        return

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

    # Memory commit (OPTION A)
    trace = MemoryTrace(
        state["ticks"],
        Z,
        coherence,
        stability,
        f"{frame.domain}:{frame.label}",
        1.0,
        ["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
    )
    memory.add_trace(trace)

    # Gate evaluation (symbolic)
    gate_engine.evaluate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        load=load,
    )

    # Pressure release
    state["structural_load"] *= 0.6

    frames.close()