# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.crystallizer import crystallize
from sandys_law_a7do.memory.decay import decay_weight

# Frozen thresholds
Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


def step_tick(state: dict, snapshot_fn):
    """
    Single authoritative tick step.
    Pure engine logic.
    No Streamlit.
    No UI.
    """

    state["ticks"] += 1

    snap = snapshot_fn()
    metrics = snap["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

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
            "frame": snap["active_frame"].label if snap["active_frame"] else "none",
        },
        weight=1.0,
        tags=["stable"] if allowed else ["unstable"],
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