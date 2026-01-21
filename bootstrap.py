# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (FREEZE-CANDIDATE)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)
- Structural load & stability divergence (Phase 5)
- Preference drift update on episode close (Phase 6)
- Attention read-through (Phase 6.1–6.3)
- Symbolic gating (Phase 7.1–7.4)

IMPORTANT:
- Gates are SYMBOLIC (allow / defer / block)
- No rewards
- No action selection
- No learning inside gates
"""

# =====================================================
# CORE STRUCTURE
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
from sandys_law_a7do.engine.tick_engine import step_tick

from sandys_law_a7do.gates.engine import GateEngine


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    # Preference system (read-only bias)
    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(
        store=pref_store,
        cfg=PreferenceConfig(),
    )

    # Gate engine (symbolic)
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

        # Tick channels (written by tick_engine)
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "last_percept_notes": [],
        "prediction_error": 0.0,
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
    gate_engine: GateEngine = state.get("gate_engine")

    active = frames.active

    # -------------------------------
    # PERCEPTION SUMMARY
    # -------------------------------
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
        block_rate=float(report.block_rate),
    )

    # -------------------------------
    # GATE SNAPSHOT (DICT-SAFE)
    # -------------------------------
    gate_view = {}
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            # gs IS A DICT — NOT A DATACLASS
            gate_view[name] = {
                "state": gs.get("state"),
                "reason": gs.get("reason"),
                "last_tick": gs.get("last_tick"),
            }

    # -------------------------------
    # PREFERENCE VIEW
    # -------------------------------
    pref_store: PreferenceStore = state["preference_store"]
    top_prefs = pref_store.top(10)

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
        "prediction_error": state.get("prediction_error"),
        "preference_top": [
            {"context": k, "score": v} for (k, v) in top_prefs
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
    Includes:
    - Memory trace
    - Preference update
    - Gate evaluation
    """

    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine = state.get("gate_engine")

    frame = frames.active
    if not frame:
        return

    # -------------------------------
    # PERCEPT SUMMARY
    # -------------------------------
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
    block_rate = float(report.block_rate)

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # -------------------------------
    # MEMORY TRACE
    # -------------------------------
    trace = MemoryTrace(
        tick=state["ticks"],
        Z=Z,
        coherence=coherence,
        stability=stability,
        frame_signature=f"{frame.domain}:{frame.label}",
        weight=1.0,
        tags=["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
    )
    memory.add_trace(trace)

    # -------------------------------
    # PREFERENCE UPDATE (READ-ONLY)
    # -------------------------------
    pref_engine: PreferenceEngine = state["preference_engine"]

    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        notes=percept.notes,
    )

    pref_update = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        prediction_error_l1=state.get("prediction_error"),
    )

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": pref_update.context_key,
        "previous": pref_update.previous,
        "updated": pref_update.updated,
        "delta": pref_update.delta,
        "reason": pref_update.reason,
    }

    # -------------------------------
    # GATE EVALUATION (SYMBOLIC)
    # -------------------------------
    if gate_engine:
        gate_engine.evaluate(
            coherence=coherence,
            fragmentation=Z,
            block_rate=block_rate,
            load=load,
        )

    # -------------------------------
    # RESOLUTION RELEASES LOAD
    # -------------------------------
    state["structural_load"] *= 0.6
    frames.close()


# =====================================================
# TICK — STRUCTURAL PRESSURE ONLY
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1

    frames = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))