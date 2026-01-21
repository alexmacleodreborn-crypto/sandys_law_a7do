# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4)
- Structural load & stability divergence (Phase 5)
- Preference drift (Phase 6 — READ-ONLY BIAS)
- Gate evaluation on episode boundary (Phase 7.4)

MemoryTrace signature (AUTHORITATIVE):
MemoryTrace(
    tick,
    Z,
    coherence,
    stability,
    frame_signature,
    weight=1.0,
    tags=[...]
)
"""

# =====================================================
# IMPORTS
# =====================================================

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

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

    # Phase 6 — preference (read-only bias)
    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(
        store=pref_store,
        cfg=PreferenceConfig(),
    )

    # Phase 7 — gates
    gate_engine = GateEngine()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # Structural pressure
        "structural_load": 0.0,

        # Preference system
        "preference_store": pref_store,
        "preference_engine": pref_engine,
        "last_preference_update": None,

        # Gates
        "gate_engine": gate_engine,
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# =====================================================
# SNAPSHOT (READ-ONLY)
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

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

    # ---- Gate snapshot ----
    gate_view = {}
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            gate_view[name] = {
                "state": gs.result.state,
                "open": gs.result.state == "allow",
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
        "last_preference_update": state.get("last_preference_update"),
    }


# =====================================================
# FRAME ACTIONS
# =====================================================

def open_frame(state: dict):
    if state["frames"].active:
        return
    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)


def add_fragment(state: dict):
    frame = state["frames"].active
    if not frame:
        return

    fragments = perceive_and_act(state)
    for frag in fragments:
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
    """
    OPTION A — EPISODE COMMIT ON FRAME CLOSE

    Phase 7.4:
    - Gates evaluated HERE and ONLY HERE
    """

    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    frame = frames.active
    if not frame:
        return

    # ---- Percept summary ----
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

    # ---------------------------------
    # Phase 7.4 — GATE EVALUATION (AUTHORITATIVE)
    # ---------------------------------
    if gate_engine:
        gate_engine.evaluate(
            coherence=coherence,
            fragmentation=Z,
            stability=stability,
            load=load,
            tick=state["ticks"],
        )

    # ---- Memory trace ----
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

    # ---- Preference update (READ-ONLY BIAS) ----
    pref_engine: PreferenceEngine = state["preference_engine"]

    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        notes=percept.notes,
    )

    update = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        prediction_error_l1=None,
    )

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": update.context_key,
        "previous": update.previous,
        "updated": update.updated,
        "delta": update.delta,
        "reason": update.reason,
    }

    # ---- Release structural pressure ----
    state["structural_load"] *= 0.6

    frames.close()


# =====================================================
# TICK — STRUCTURAL LOAD ONLY
# =====================================================

def tick_system(state: dict):
    """
    Phase 5 — Temporal structural pressure
    """
    state["ticks"] += 1

    frames = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))