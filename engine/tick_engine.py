# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.crystallizer import crystallize
from sandys_law_a7do.memory.decay import decay_weight

# --------------------------------------------------
# Frozen regulation thresholds
# --------------------------------------------------
Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


def step_tick(state: dict, snapshot_fn):
    """
    Single authoritative tick step.
    Matches the REAL MemoryTrace schema.
    """

    state["ticks"] += 1

    snap = snapshot_fn()
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    frame_signature = (
        snap["active_frame"].label
        if snap["active_frame"] is not None
        else "none"
    )

    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    # --------------------------------------------------
    # MEMORY TRACE — MATCHES ACTUAL CLASS
    # --------------------------------------------------
    trace = MemoryTrace(
        state["ticks"],      # tick
        Z,                   # fragmentation
        coherence,           # coherence
        stability,           # stability
        frame_signature,     # REQUIRED
    )

    if allowed:
        state["stable_ticks"] += 1
        state["memory"].add_trace(trace)

        if state["stable_ticks"] >= MEMORY_PERSIST_TICKS:
            crystallize(state["memory"])
    else:
        state["stable_ticks"] = 0
        decay_weight(state["memory"])

    return trace