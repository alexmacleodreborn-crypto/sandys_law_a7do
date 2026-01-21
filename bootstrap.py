def close_frame(state: dict):
    """
    OPTION A — EPISODE COMMIT POINT (FIXED)
    """
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    # --- final snapshot BEFORE closing ---
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

    # --- commit EPISODE memory (VALID CONSTRUCTOR) ---
    trace = MemoryTrace(
        state["ticks"],                 # trace_id
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

    # --- now close frame (reset is correct) ---
    frames.close()