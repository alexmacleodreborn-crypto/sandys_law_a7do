"""
Bootstrap v1.3 — A7DO Core

Single source of truth for:
- Frames
- Metrics
- Regulation
- Memory
- Time
"""

# =====================================================
# CORE
# =====================================================

from .frames.store import FrameStore
from .frames.frame import Frame
from .frames.fragment import Fragment

from .mind.coherence import compute_coherence
from .mind.regulation import regulate

# =====================================================
# MEMORY
# =====================================================

from .memory.trace import MemoryTrace
from .memory.structural_memory import StructuralMemory
from .memory.crystallizer import crystallize
from .memory.decay import decay_weight

# =====================================================
# PERCEPTION (Phase 4.1)
# =====================================================

from .integration.perception_loop import perceive_and_act

# =====================================================
# REGULATION CONSTANTS (FROZEN)
# =====================================================

Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3

# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    state = {
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "ticks": 0,
        "stable_ticks": 0,

        # Metric history (ONLY written here)
        "metric_history": {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        },

        # Visual markers
        "crystallisation_ticks": [],
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


# =====================================================
# SNAPSHOT (READ-ONLY)
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
    if state["frames"].active:
        return
    state["frames"].open(Frame(domain="demo", label="ui"))

def close_frame(state: dict):
    state["frames"].close()


# =====================================================
# TICK (ONLY PLACE STATE MUTATES OVER TIME)
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1

    # ---------------------------------------------
    # PERCEPTION → FRAGMENTS
    # ---------------------------------------------
    if state["frames"].active:
        for frag in perceive_and_act(state):
            state["frames"].add_fragment(frag)

    # ---------------------------------------------
    # METRICS
    # ---------------------------------------------
    snap = system_snapshot(state)
    m = snap["metrics"]

    Z = m["Z"]
    coherence = m["Coherence"]
    stability = m["Stability"]

    # ---------------------------------------------
    # RECORD HISTORY (CRITICAL)
    # ---------------------------------------------
    hist = state["metric_history"]
    hist["ticks"].append(state["ticks"])
    hist["Z"].append(Z)
    hist["Coherence"].append(coherence)
    hist["Stability"].append(stability)

    # ---------------------------------------------
    # REGULATION
    # ---------------------------------------------
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
            clusters = state["memory"].clusters()
            if clusters:
                crystallize(state["memory"])
                state["crystallisation_ticks"].append(state["ticks"])
            state["stable_ticks"] = 0
    else:
        state["stable_ticks"] = 0
        decay_weight(state["memory"])