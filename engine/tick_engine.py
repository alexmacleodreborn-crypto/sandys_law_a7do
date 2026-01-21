# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.integration.perception_loop import perceive_and_act


def step_tick(state, snapshot):
    """
    Single system tick.

    Phase 5.2 → 6.2:
    - Structural prediction error
    - Preference drift (global, cumulative)
    - Continuous perception (adds fragments each tick if frame is active)
    - NO reward
    - NO action selection
    - NO memory commit here (Option A)
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    frames = state["frames"]
    frame = frames.active

    # ---------------------------------
    # PERCEPTION SUMMARY (OF CURRENT FRAME)
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
        prediction_error = 0.25  # first exposure novelty

    state["last_percept"] = {
        "fragment_count": fragment_count,
        "unique_actions": unique_actions,
        "notes": percept_notes,
    }
    state["prediction_error"] = prediction_error

    # ---------------------------------
    # METRICS
    # ---------------------------------
    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    block_rate = float(report.block_rate)

    # Expose for perception loop (attention coupling)
    state["last_fragmentation"] = Z
    state["last_coherence"] = coherence
    state["last_block_rate"] = block_rate
    state["last_percept_notes"] = percept_notes

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # ---------------------------------
    # PREFERENCE UPDATE (USE EXISTING ENGINE)
    # ---------------------------------
    # IMPORTANT: do NOT create a new PreferenceEngine here.
    # It must be created in bootstrap and stored in state.
    pref_engine = state.get("preference_engine")

    if pref_engine is not None:
        context_key = pref_engine.context_key_from_accounting(
            coherence=coherence,
            fragmentation=Z,
            block_rate=block_rate,
            notes=percept_notes,
        )

        update = pref_engine.update(
            context_key=context_key,
            coherence=coherence,
            fragmentation=Z,
            block_rate=block_rate,
            prediction_error_l1=prediction_error,
        )

        state["last_preference_update"] = {
            "tick": state["ticks"],
            "context": update.context_key,
            "previous": update.previous,
            "updated": update.updated,
            "delta": update.delta,
            "reason": update.reason,
        }

    # ---------------------------------
    # CONTINUOUS PERCEPTION (KEY FIX)
    # ---------------------------------
    # This is why attention only showed after "New Frame" before:
    # you were not generating new fragments with updated attention each tick.
    if frame:
        new_frags = perceive_and_act(state)
        for f in new_frags:
            frames.add_fragment(f)