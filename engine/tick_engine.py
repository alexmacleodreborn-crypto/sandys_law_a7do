from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.preference import PreferenceEngine


def step_tick(state, snapshot):
    """
    Single system tick.

    Phase 5.2-B:
    - Structural prediction error (already present)
    - Preference drift driven by prediction error
    - NO reward
    - NO action selection
    - NO memory commit here (Option A)
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    # Ensure preference engine exists (lazy, safe)
    state.setdefault("preference_engine", PreferenceEngine())
    pref_engine = state["preference_engine"]

    frames = state["frames"]
    frame = frames.active

    # ---------------------------------
    # PERCEPTION (ONLY IF FRAME ACTIVE)
    # ---------------------------------
    if frame:
        fragments = [{"action": f.kind} for f in frame.fragments]
        percept = summarize_perception(fragments)

        fragment_count = percept.fragment_count
        unique_actions = percept.unique_actions
        percept_notes = percept.notes
    else:
        fragment_count = 0
        unique_actions = 0
        percept_notes = ["empty"]

    # ---------------------------------
    # STRUCTURAL PREDICTION ERROR
    # ---------------------------------
    last = state.get("last_percept")

    if last:
        pe_frag = abs(fragment_count - last["fragment_count"])
        pe_act = abs(unique_actions - last["unique_actions"])
        prediction_error = min(1.0, (pe_frag + pe_act) / 6.0)
    else:
        prediction_error = 0.25

    # Store percept for next tick
    state["last_percept"] = {
        "fragment_count": fragment_count,
        "unique_actions": unique_actions,
        "notes": percept_notes,
    }

    state["prediction_error"] = prediction_error

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
    block_rate = float(report.block_rate)
    stability = coherence * (1.0 - block_rate)

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # ---------------------------------
    # PREFERENCE UPDATE (KEY STEP)
    # ---------------------------------
    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        notes=percept_notes,
    )

    pref_update = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        prediction_error_l1=prediction_error,
    )

    # Expose for dashboards / inspection
    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": pref_update.context_key,
        "previous": pref_update.previous,
        "updated": pref_update.updated,
        "delta": pref_update.delta,
        "reason": pref_update.reason,
    }

    # NOTE:
    # - No memory write here
    # - No forgetting
    # - No action choice