# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.2 (FROZEN)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close

No rewards
No time
No semantics
"""

# =====================================================
# CORE STRUCTURE
# =====================================================

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory


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


# =====================================================
# FRAME ACTIONS
# =====================================================

def open_frame(state: dict):
    if state["frames"].active:
        return

    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)


def add_fragment(state: dict):
    if not state["frames"].active:
        return

    frag = Fragment(kind="demo")
    state["frames"].add_fragment(frag)


def close_frame(state: dict):
    """
    OPTION A — EPISODE COMMIT ON FRAME CLOSE
    """
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    # -----------------------------
    # FINAL FRAME SNAPSHOT
    # -----------------------------
    fragment_count = len(frame.fragments)
    unique_actions = len(set(f.kind for f in frame.fragments))

    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    stability = coherence * (1.0 - float(report.block_rate))

    # -----------------------------
    # EPISODE MEMORY TRACE
    # (MATCHES ACTUAL MemoryTrace)
    # -----------------------------
    trace = MemoryTrace(
        state["ticks"],   # trace_id
        {
            "frame": f"{frame.domain}:{frame.label}",
            "Z": Z,
            "coherence": coherence,
            "stability": stability,
            "fragments": fragment_count,
            "unique_kinds": unique_actions,
        },
        tags=["episode", "stable"] if coherence >= 0.7 else ["episode", "unstable"],
    )

    memory.add_trace(trace)

    # -----------------------------
    # CLOSE FRAME (RESET IS CORRECT)
    # -----------------------------
    frames.close()


# =====================================================
# TICK (UNCHANGED)
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1