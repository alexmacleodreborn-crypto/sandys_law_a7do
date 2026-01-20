# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.1
Adds gated structural memory on top of frozen v1.0 core
"""

from typing import Tuple, Callable

# -----------------------------
# Core systems
# -----------------------------
from frames.store import FrameStore
from frames.frame import Frame
from frames.fragment import Fragment

from sandy_law.coherence_law import compute_coherence
from sandy_law.collapse_conditions import regulate

# -----------------------------
# Memory (v1.1)
# -----------------------------
from memory.trace import Trace
from memory.structural_memory import StructuralMemory
from memory.crystallizer import crystallize
from memory.decay import decay_memory

# -----------------------------
# Regulation thresholds (frozen)
# -----------------------------
Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


# =====================================================
# System build
# =====================================================

def build_system() -> Tuple[object, Callable, dict]:
    frames = FrameStore()
    memory = StructuralMemory()
    state = {
        "ticks": 0,
        "frames": frames,
        "memory": memory,
        "stable_ticks": 0,
    }

    def snapshot():
        return system_snapshot(state)

    return state, snapshot, state


# =====================================================
# Snapshot
# =====================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    active = frames.active

    # -----------------------------
    # Compute metrics (v1.0)
    # -----------------------------
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

    regulation = regulate(metrics)

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "regulation": regulation,
        "active_frame": active,
        "memory_count": len(memory.memories),
    }


# =====================================================
# Frame helpers
# =====================================================

def inject_demo_frame(state: dict):
    frame = Frame(domain="world", label="demo")
    state["frames"].open(frame)


def add_fragment_by_kind(state: dict, kind: str):
    fragment = Fragment(kind=kind)
    state["frames"].add_fragment(fragment)


def close_frame(state: dict):
    state["frames"].close()


# =====================================================
# Tick (v1.1 memory integration)
# =====================================================

def tick_system(state: dict):
    """
    v1.0 behaviour preserved.
    v1.1 adds gated memory downstream.
    """

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

    # -----------------------------
    # Build trace (always)
    # -----------------------------
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

    # -----------------------------
    # Memory gate
    # -----------------------------
    if allowed:
        state["stable_ticks"] += 1
        state["memory"].add_trace(trace)

        if state["stable_ticks"] >= MEMORY_PERSIST_TICKS:
            crystallize(state["memory"])

    else:
        state["stable_ticks"] = 0
        decay_memory(state["memory"])


# =====================================================
# Experiment helpers (unchanged)
# =====================================================

def add_fragment(state: dict):
    add_fragment_by_kind(state, "demo")