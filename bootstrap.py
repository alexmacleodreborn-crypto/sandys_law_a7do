# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.4.1 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)

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

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory

# Phase 4.1 perceptual loop
from sandys_law_a7do.integration.perception_loop import perceive_and_act


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
        fragments = [{"action": f.kind} for f in active.fragments]
        percept = summarize_perception(fragments)
    else:
        percept = summarize_perception([])

    report = compute_coherence(
        fragment_count=percept.fragment_count,
        unique_actions=percept.unique_actions,
        blocked_events=0,
        percept_notes=percept.notes,   # 🔑 Phase 4.2 coupling
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
    """
    Phase 4.1 — Controlled Perceptual Diversity

    Introduces:
    - Small structural variation
    - No semantics
    - No reward
    - No goals
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
    (MATCHES REAL MemoryTrace)
    """
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    # -----------------------------
    # FINAL FRAME SNAPSHOT
    # -----------------------------
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
    stability = coherence * (1.0 - float(report.block_rate))

    # -----------------------------
    # EPISODE MEMORY TRACE (POSITIONAL)
    # -----------------------------
    trace = MemoryTrace(
        state["ticks"],                  # tick
        Z,                               # fragmentation
        coherence,                       # coherence
        stability,                       # stability
        f"{frame.domain}:{frame.label}", # frame_signature
        1.0,                             # weight
        ["episode", "stable"] if coherence >= 0.7 else ["episode", "unstable"],
    )

    memory.add_trace(trace)

    # -----------------------------
    # CLOSE FRAME (RESET IS CORRECT)
    # -----------------------------
    frames.close()


# =====================================================
# TICK (UNCHANGED / PURE)
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1