"""
Bootstrap — v1.2
A7DO Core Wiring with Embodied Perception + Metric History

This file is the SINGLE source of truth for:
- System state
- Tick evolution
- Regulation
- Memory gating
"""

# =====================================================
# CORE SYSTEMS
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
# PERCEPTION LOOP (Phase 4.1)
# =====================================================

from .integration.perception_loop import perceive_and_act

# =====================================================
# REGULATION THRESHOLDS (FROZEN)
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

        # ✅ Persistent metric history (UI + analysis)
        "metric_history": {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        },

        # Optional visual markers
        "crystallisation_ticks": [],
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

    # --------------------------------------------------
    # CoherenceReport (source of truth)
    # --------------------------------------------------

    report: CoherenceReport = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    # --------------------------------------------------
    # Sandy’s Law metric mapping
    # --------------------------------------------------

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    stability = coherence * (1.0 - float(report.block_rate))

    # --------------------------------------------------
    # Regulation decision
    # --------------------------------------------------

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
        return None

    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)
    return frame

def add_fragment_by_kind(state: dict, kind: str):
    frag = Fragment(kind=kind)
    state["frames"].add_fragment(frag)
    return frag

def close_frame(state: dict):
    return state["frames"].close()

# =====================================================
# TICK + MEMORY GATING
# =====================================================

def tick_system(state: dict):
    state["ticks"] += 1

    # ---------------------------------------------
    # EMBODIED PERCEPTION (AUTO-FRAGMENTS)
    # ---------------------------------------------
    if state["frames"].active:
        fragments = perceive_and_act(state)
        for frag in fragments:
            state["frames"].add_fragment(frag)

    # ---------------------------------------------
    # SNAPSHOT + METRICS
    # ---------------------------------------------
    snap = system_snapshot(state)
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    # ---------------------------------------------
    # RECORD METRIC HISTORY (THIS FIXES THE PLOT)
    # ---------------------------------------------
    hist = state["metric_history"]
    hist["ticks"].append(state["ticks"])
    hist["Z"].append(Z)
    hist["Coherence"].append(coherence)
    hist["Stability"].append(stability)

    # ---------------------------------------------
    # REGULATION GATE
    # ---------------------------------------------
    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    # ---------------------------------------------
    # MEMORY TRACE
    # ---------------------------------------------
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
            state["stable_ticks"] = 0
    else:
        state["stable_ticks"] = 0
        decay_weight(state["memory"])