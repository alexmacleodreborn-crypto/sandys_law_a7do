"""
Bootstrap — v1.2
A7DO Sandy’s Law Core
Streamlit-safe, frame-stable, perception-driven
"""

# =====================================================
# CORE STRUCTURES
# =====================================================

from .frames.store import FrameStore
from .frames.frame import Frame
from .frames.fragment import Fragment

from .mind.coherence import compute_coherence, CoherenceReport
from .mind.regulation import regulate

# =====================================================
# MEMORY
# =====================================================

from .memory.trace import MemoryTrace
from .memory.structural_memory import StructuralMemory
from .memory.crystallizer import crystallize
from .memory.decay import decay_weight

# =====================================================
# PERCEPTION
# =====================================================

from .integration.perception_loop import perceive_and_act

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
        "history": {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        },
        "crystallisation_ticks": [],
    }

    def snapshot():
        return system_snapshot(state)

    return None, snapshot, state


# =====================================================
# FRAME SAFETY (CRITICAL FOR STREAMLIT)
# =====================================================

def ensure_active_frame(state: dict):
    """
    Streamlit-safe guarantee that a frame exists.
    Idempotent across reruns.
    """
    if state["frames"].active is None:
        frame = Frame(domain="demo", label="ui")
        state["frames"].open(frame)


def inject_demo_frame(state: dict):
    ensure_active_frame(state)


def close_frame(state: dict):
    state["frames"].close()


def add_fragment_by_kind(state: dict, kind: str):
    ensure_active_frame(state)
    frag = Fragment(kind=kind)
    state["frames"].add_fragment(frag)
    return frag


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

    # ----------------------------------------------
    # COHERENCE REPORT (SOURCE OF TRUTH)
    # ----------------------------------------------

    report: CoherenceReport = compute_coherence(
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
        "memory_count": state["memory"].count(),
    }


# =====================================================
# TICK (THE HEART)
# =====================================================

def tick_system(state: dict):
    """
    One structural tick.
    - Guarantees frame
    - Runs perception
    - Updates metrics
    - Gates memory
    """

    # ----------------------------------------------
    # CRITICAL: FRAME MUST EXIST ON EVERY RERUN
    # ----------------------------------------------
    ensure_active_frame(state)

    state["ticks"] += 1

    frame = state["frames"].active

    # ----------------------------------------------
    # PERCEPTION → FRAGMENTS
    # ----------------------------------------------
    new_fragments = perceive_and_act(state)

    for frag in new_fragments:
        frame.add(frag)

    # ----------------------------------------------
    # METRICS
    # ----------------------------------------------
    snap = system_snapshot(state)
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    # ----------------------------------------------
    # HISTORY (FOR PLOTTING)
    # ----------------------------------------------
    state["history"]["ticks"].append(state["ticks"])
    state["history"]["Z"].append(Z)
    state["history"]["Coherence"].append(coherence)
    state["history"]["Stability"].append(stability)

    # ----------------------------------------------
    # REGULATION GATE
    # ----------------------------------------------
    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    # ----------------------------------------------
    # MEMORY TRACE (MATCHES YOUR SCHEMA)
    # ----------------------------------------------
    trace = MemoryTrace(
        trace_id=state["ticks"],
        features={
            "Z": Z,
            "coherence": coherence,
            "stability": stability,
            "fragment_count": len(frame.fragments),
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