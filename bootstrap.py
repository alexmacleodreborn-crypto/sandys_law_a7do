"""
Bootstrap — v1.2 (STABLE)

Responsibilities:
- Owns all system state
- Enforces structural order (Frame → Fragment → Tick)
- No UI logic
"""

# =====================================================
# CORE STRUCTURES
# =====================================================

from .frames.store import FrameStore
from .frames.frame import Frame
from .frames.fragment import Fragment

from .mind.coherence import compute_coherence
from .mind.regulation import regulate

from .memory.trace import MemoryTrace
from .memory.structural_memory import StructuralMemory
from .memory.crystallizer import crystallize
from .memory.decay import decay_weight


# =====================================================
# FROZEN REGULATION THRESHOLDS
# =====================================================

Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,
        "stable_ticks": 0,
        "metric_history": {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        },
        "crystallisation_ticks": [],
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# =====================================================
# SNAPSHOT (PURE READ)
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames = state["frames"]
    memory = state["memory"]

    active = frames.active

    if active:
        fragment_count = len(active.fragments)
        unique_actions = len(set(f.kind for f in active.fragments))
    else:
        fragment_count = 0
        unique_actions = 0

    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    stability = coherence * (1.0 - report.block_rate)

    regulation = regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=report.block_rate,
    )

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
        },
        "regulation": regulation,
        "active_frame": active,
        "memory_count": memory.count(),
    }


# =====================================================
# FRAME ACTIONS
# =====================================================

def inject_demo_frame(state: dict):
    if state["frames"].active is not None:
        return None

    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)
    return frame


def add_fragment_by_kind(state: dict, kind: str):
    frames = state["frames"]

    if frames.active is None:
        return None  # ← critical safety fix

    frag = Fragment(kind=kind)
    frames.add_fragment(frag)
    return frag


def close_frame(state: dict):
    return state["frames"].close()


# =====================================================
# TICK + MEMORY
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1

    snap = system_snapshot(state)
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    # record metric history
    hist = state["metric_history"]
    hist["ticks"].append(state["ticks"])
    hist["Z"].append(Z)
    hist["Coherence"].append(coherence)
    hist["Stability"].append(stability)

    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    trace = MemoryTrace(
        trace_id=state["ticks"],
        features={
            "Z": Z,
            "coherence": coherence,
            "stability": stability,
        },
    )

    if allowed:
        state["stable_ticks"] += 1
        state["memory"].add_trace(trace)

        if state["stable_ticks"] >= MEMORY_PERSIST_TICKS:
            crystallize(state["memory"])
            state["crystallisation_ticks"].append(state["ticks"])
    else:
        state["stable_ticks"] = 0
        decay_weight(state["memory"])