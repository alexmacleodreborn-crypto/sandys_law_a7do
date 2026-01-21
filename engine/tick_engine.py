# sandys_law_a7do/engine/tick_engine.py

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
    - MATCHES REAL MemoryTrace SIGNATURE (POSITIONAL)
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
    # FRAME SIGNATURE (SAFE)
    # ---------------------------------
    frame = data.get("active_frame")
    frame_signature = (
        f"{frame.domain}:{frame.label}"
        if frame is not None
        else "none"
    )

    # ---------------------------------
    # CREATE MEMORY TRACE (POSITIONAL)
    # ---------------------------------
    trace = MemoryTrace(
        state["ticks"],     # tick
        Z,                  # fragmentation
        coherence,           # coherence
        stability,           # stability
        frame_signature,     # frame signature
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