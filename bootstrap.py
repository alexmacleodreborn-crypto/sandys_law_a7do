# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.6.1 (LOCKED)

Adds:
- Phase 6.2: READ-ONLY attention aggregation

DOES NOT:
- Change memory rules
- Change preference logic
- Change perception loop
- Introduce actions or reward
"""

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

    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(store=pref_store, cfg=PreferenceConfig())

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,
        "structural_load": 0.0,
        "preference_engine": pref_engine,
        "preference_store": pref_store,
        "last_preference_update": None,
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

    # --------------------------------------------------
    # Phase 6.2 — ATTENTION AGGREGATION (READ-ONLY)
    # --------------------------------------------------
    if active:
        attention_values = [
            f.payload.get("attention", 0.0)
            for f in active.fragments
            if isinstance(f.payload, dict)
        ]
        attention = sum(attention_values) / max(1, len(attention_values))
    else:
        attention = 0.0

    pref_store: PreferenceStore = state["preference_store"]
    top_contexts = pref_store.top(10)

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
            "Attention": attention,   # ✅ NEW, SAFE
        },
        "regulation": regulation,
        "active_frame": active,
        "memory_count": memory.count(),
        "preference_top": [{"context": k, "score": v} for (k, v) in top_contexts],
        "last_preference_update": state.get("last_preference_update"),
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

    fragments = perceive_and_act(state)
    for frag in fragments:
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
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
# TICK — Phase 5
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