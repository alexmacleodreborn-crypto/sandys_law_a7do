# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Structural load & stability divergence (Phase 5)
- Preference drift (Phase 6, READ-ONLY)
- Gate inertia & pressure (Phase 7.4)

NO reward
NO action selection
NO forgetting
"""

# =====================================================
# CORE IMPORTS
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

        # Phase 5
        "structural_load": 0.0,

        # Phase 6
        "preference_store": pref_store,
        "preference_engine": pref_engine,
        "last_preference_update": None,

        # Phase 7
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
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=report.block_rate,
    )

    # -----------------------------
    # Gates snapshot
    # -----------------------------
    gates = {}
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            gates[name] = {
                "open": gs.open,
                "score": round(gs.score, 3),
                "pressure": round(gs.pressure, 3),
                "reason": gs.reason,
            }

    # -----------------------------
    # Preferences (read-only)
    # -----------------------------
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
        "active_frame": active,
        "memory_count": memory.count(),

        # Phase 6
        "preference_top": [{"context": k, "score": v} for k, v in top_prefs],
        "last_preference_update": state.get("last_preference_update"),

        # Phase 7
        "gates": gates,
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
        frame.fragments.append(frag)


def close_frame(state: dict):
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    pref_engine: PreferenceEngine = state["preference_engine"]

    frame = frames.active
    if not frame:
        return

    fragments = [{"action": f.kind} for f in frame.fragments]
    percept = summarize_perception(fragments)

    report = compute_coherence(
        fragment_count=percept.fragment_count,
        unique_actions=percept.unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

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

    # Preference update (bias only)
    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        notes=percept.notes,
    )

    upd = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        prediction_error_l1=None,
    )

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": upd.context_key,
        "previous": upd.previous,
        "updated": upd.updated,
        "delta": upd.delta,
        "reason": upd.reason,
    }

    state["structural_load"] *= 0.6
    frames.close()


# =====================================================
# TICK — STRUCTURAL PRESSURE + GATES
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

    # ---- Gate step ----
    gate_engine: GateEngine = state.get("gate_engine")
    if gate_engine:
        gate_engine.step(
            context={
                "load": state["structural_load"],
                "frame_open": frames.active is not None,
            },
            tick=state["ticks"],
        )