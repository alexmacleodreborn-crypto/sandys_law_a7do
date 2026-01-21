from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate

from sandys_law_a7do.mind.expectation import ExpectationModel
from sandys_law_a7do.mind.prediction_error import compute_prediction_error_l1
from sandys_law_a7do.mind.preference import PreferenceEngine


def step_tick(state, snapshot):
    """
    Single system tick.

    Phase 5.1:
    - Perception
    - Structural metrics
    - Prediction error
    - Preference drift (NO reward, NO action)
    - Regulation is read-only
    - Memory commit happens ONLY on frame close (Option A)
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    # Ensure long-lived models exist
    state.setdefault("expectation", ExpectationModel())
    state.setdefault("preference_engine", PreferenceEngine())

    expectation = state["expectation"]
    preference_engine = state["preference_engine"]

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
        notes = percept.notes
    else:
        fragment_count = 0
        unique_actions = 0
        notes = ["empty"]

    # ---------------------------------
    # STRUCTURAL METRICS
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
    # EXPECTATION & PREDICTION ERROR
    # ---------------------------------
    expected = expectation.predict(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
    )

    observed = {
        "fragment_count": fragment_count,
        "unique_actions": unique_actions,
    }

    prediction_error_l1 = compute_prediction_error_l1(
        expected=expected,
        observed=observed,
    )

    # Update expectation AFTER measuring error
    expectation.update(observed)

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # ---------------------------------
    # PREFERENCE UPDATE (NO ACTION)
    # ---------------------------------
    context_key = preference_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        notes=notes,
    )

    pref_update = preference_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        prediction_error_l1=prediction_error_l1,
    )

    # ---------------------------------
    # STORE LAST UPDATE (FOR DASHBOARD)
    # ---------------------------------
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
    # - No action selection
    # - No forgetting
    # - No exploration bias yet