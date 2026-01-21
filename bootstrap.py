"""
Bootstrap — v1.6 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)
- Structural load & stability divergence (Phase 5)
- Preference drift update on episode close (Phase 6) — READ-ONLY BIAS
- Gate engine integration (Phase 7.3)

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
# CORE STRUCTURE
# =====================================================

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.perception import summarize_perception

from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory

from sandys_law_a7do.integration.perception_loop import perceive_and_act


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    # Phase 6 — preference (in-memory)
    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(
        store=pref_store,
        cfg=PreferenceConfig(),
    )

    # -------------------------------------------------
    # 🔑 CRITICAL FIX — LAZY IMPORT (breaks circular import)
    # -------------------------------------------------
    from sandys_law_a7do.gates.engine import GateEngine
    gate_engine = GateEngine()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # Phase 5 — temporal structural pressure
        "structural_load": 0.0,

        # Phase 6 — preference system (READ-ONLY bias)
        "preference_engine": pref_engine,
        "preference_store": pref_store,
        "last_preference_update": None,

        # Phase 7 — gate system
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

    # Phase 6 — preference visibility
    pref_store: PreferenceStore = state["preference_store"]
    top_contexts = pref_store.top(10)

    # Phase 7 — gate snapshot (SAFE)
    gate_engine = state.get("gate_engine")
    gate_snapshot = gate_engine.snapshot() if gate_engine else None

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
            {"context": k, "score": v}
            for (k, v) in top_contexts
        ],
        "last_preference_update": state.get("last_preference_update"),

        # Phase 7
        "gates": gate_snapshot,
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
    """
    Phase 4.1 — Controlled Perceptual Diversity
    """
    frame = state["frames"].active
    if not frame:
        return

    fragments = perceive_and_act(state)
    for frag in fragments:
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
    """
    OPTION A — EPISODE COMMIT ON FRAME CLOSE
    + Phase 6 Preference Update
    """
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

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

    # Phase 6 — preference update
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

    state["structural_load"] *= 0.6
    frames.close()


# =====================================================
# TICK — Phase 5 Structural Load
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