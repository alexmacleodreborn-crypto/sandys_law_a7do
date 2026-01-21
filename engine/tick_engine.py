# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.memory.trace import MemoryTrace

# --------------------------------------------------
# REGULATION THRESHOLDS (FROZEN)
# --------------------------------------------------
Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7


def step_tick(state: dict, snapshot):
    """
    Advance system by one tick.

    - Always records experience (trace_log)
    - Only consolidates memory if regulation allows
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    data = snapshot()
    metrics = data["metrics"]

    Z = metrics["Z"]
    coherence = metrics["Coherence"]
    stability = metrics["Stability"]

    # ---------------------------------
    # REGULATION DECISION
    # ---------------------------------
    allowed = (
        Z < Z_MAX
        and coherence >= COHERENCE_MIN
        and stability >= STABILITY_MIN
    )

    # ---------------------------------
    # CREATE MEMORY TRACE
    # (MATCHES MemoryTrace SIGNATURE)
    # ---------------------------------
    trace = MemoryTrace(
        state["ticks"],              # trace_id
        {
            "Z": Z,
            "coherence": coherence,
            "stability": stability,
        },
        weight=1.0,
        tags=["stable"] if allowed else ["unstable"],
    )

    # ---------------------------------
    # ALWAYS RECORD EXPERIENCE
    # ---------------------------------
    state["memory"].trace_log.append(trace)

    # ---------------------------------
    # ONLY CONSOLIDATE IF ALLOWED
    # ---------------------------------
    if allowed:
        state["memory"].add_trace(trace)