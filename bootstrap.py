# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.1
Structural Regulation Core (v1.0) + Gated Memory (v1.1)
"""

# =====================================================
# CORE SYSTEMS
# =====================================================

from frames.store import FrameStore
from frames.frame import Frame
from frames.fragment import Fragment

from mind.coherence import compute_coherence
from mind.regulation import regulate

# =====================================================
# MEMORY (v1.1)
# =====================================================

from memory.trace import Trace
from memory.structural_memory import StructuralMemory
from memory.crystallizer import crystallize
from memory.decay import decay_memory


# =====================================================
# REGULATION THRESHOLDS (FROZEN v1.0)
# =====================================================

Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames_store = FrameStore()
    memory = StructuralMemory()

    state = {
        "frames": frames_store,
        "memory": memory,
        "ticks": 0,
        "stable_ticks": 0,
    }

    def snapshot():
        return system_snapshot(state)

    return None, snapshot, state


# =====================================================
# SNAPSHOT
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    active = frames.active

    if active:
        fragment_count = len(active.fragments)
        unique_actions = len(set(f.kind for f in active.fragments))
    else:
        fragment_count = 0
        unique_actions = 0

    metrics = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    regulation = regulate(
        coherence=metrics["Coherence"],
        fragmentation=metrics["Z"],
        block_rate=0.0,
    )

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "regulation": regulation,
        "active_frame": active,
        "memory_count": len(memory.memories),
    }


# =====================================================
# FRAME ACTIONS
# =====================================================

def inject_demo_frame(state: dict):
    if state["frames"].active:
        return None

    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)
    return frame


def add_fragment_by_kind(state: dict, kind: str):
    frag = Fragment(kind=kind, payload={"source": "experiment"})
    state["frames"].add_fragment(frag)
    return frag


def close_frame(state: dict):
    return state["frames"].close()


# =====================================================
# TICK + MEMORY GATING (v1.1)
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1

    snap = system_snapshot(state)
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    trace = Trace(
        tick=state["ticks"],
        Z=Z,
        coherence=coherence,
        stability=stability,
        frame_signature=(
            snap["active_frame"].label
            if snap["active_frame"]
            else "none"
        ),
    )

    if allowed:
        state["stable_ticks"] += 1
        state["memory"].add_trace(trace)

        if state["stable_ticks"] >= MEMORY_PERSIST_TICKS:
            crystallize(state["memory"])
    else:
        state["stable_ticks"] = 0
        decay_memory(state["memory"])