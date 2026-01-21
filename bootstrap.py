# sandys_law_a7do/bootstrap.py
"""
A7DO Bootstrap — FINAL STABLE CORE
"""

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate

from sandys_law_a7do.memory.structural_memory import StructuralMemory


# --------------------------------------------------
# SYSTEM BUILD
# --------------------------------------------------

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,
        "stable_ticks": 0,
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# --------------------------------------------------
# SNAPSHOT (PURE)
# --------------------------------------------------

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

    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    stability = coherence * (1.0 - float(report.block_rate))

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


# --------------------------------------------------
# FRAME ACTIONS
# --------------------------------------------------

def open_frame(state: dict):
    if state["frames"].active:
        return
    state["frames"].open(Frame(domain="demo", label="ui"))


def add_fragment(state: dict, kind="demo"):
    if not state["frames"].active:
        return
    state["frames"].add_fragment(Fragment(kind=kind))


def close_frame(state: dict):
    state["frames"].close()