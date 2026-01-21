# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.5 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)
- Structural load & stability divergence (Phase 5)

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

        # Phase 5 — temporal structural pressure
        "structural_load": 0.0,
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

    load = state.get("structural_load", 0.0)

    # Phase 5 — stability diverges from coherence
    stability = coherence * (1.0 - load)

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

    load = state.get("structural_load", 0.0)
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

    # Resolution releases pressure
    state["structural_load"] *= 0.6

    frames.close()


# =====================================================
# TICK — Phase 5 Structural Load
# =====================================================

def tick_system(state: dict):
    """
    Phase 5 — Temporal structural pressure

    - Load increases when a frame remains open
    - Load decays when no frame is active
    """
    state["ticks"] += 1

    frames = state["frames"]
    load = state.get("structural_load", 0.0)

    if frames.active:
        # Unresolved persistence accumulates cost
        load += 0.05
    else:
        # Rest releases pressure
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))