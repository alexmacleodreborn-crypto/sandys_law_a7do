from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate


def step_tick(state, snapshot):
    """
    Single system tick.
    Perception → metrics → regulation.
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
    else:
        fragment_count = 0
        unique_actions = 0

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

    # NOTE:
    # - No memory write here
    # - Memory happens ONLY on close_frame (Option A)