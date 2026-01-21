from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate


def step_tick(state, snapshot):
    """
    Single system tick.
    Perception → metrics → regulation.
    Phase 5.2: Structural prediction error.
    No memory commit here (Option A).
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    frames = state["frames"]
    frame = frames.active

    # ---------------------------------
    # PERCEPTION (ONLY IF FRAME ACTIVE)
    # ---------------------------------
    if frame:
        fragments = [
            {"action": f.kind}
            for f in frame.fragments
        ]

        percept = summarize_perception(fragments)

        fragment_count = percept.fragment_count
        unique_actions = percept.unique_actions
        percept_notes = percept.notes
    else:
        fragment_count = 0
        unique_actions = 0
        percept_notes = []

    # ---------------------------------
    # STRUCTURAL PREDICTION ERROR (NEW)
    # ---------------------------------
    last = state.get("last_percept")

    if last:
        # L1-style mismatch across structural dimensions
        pe_frag = abs(fragment_count - last["fragment_count"])
        pe_act = abs(unique_actions - last["unique_actions"])

        # Normalize conservatively
        prediction_error = min(1.0, (pe_frag + pe_act) / 6.0)
    else:
        # First exposure = moderate novelty
        prediction_error = 0.25

    # Store percept for next tick
    state["last_percept"] = {
        "fragment_count": fragment_count,
        "unique_actions": unique_actions,
        "notes": percept_notes,
    }

    # ---------------------------------
    # METRICS (STRUCTURAL ONLY)
    # ---------------------------------
    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    stability = coherence * (1.0 - float(report.block_rate))

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=report.block_rate,
    )

    # ---------------------------------
    # EXPORT TO STATE (FOR PREFERENCE LOOP)
    # ---------------------------------
    state["prediction_error"] = prediction_error

    # NOTE:
    # - No memory write here
    # - No preference update here
    # - Memory happens ONLY on close_frame (Option A)