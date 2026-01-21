# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

# 🔑 Phase 7.1
from sandys_law_a7do.accounting.expectation import (
    ExpectationEngine,
    ExpectationStore,
)


def step_tick(state, snapshot):
    """
    Phase 7.2 — Expectation-driven prediction error

    - Builds observed structural vector
    - Looks up expectation by context key
    - Computes PE = |observed - expected|
    - Falls back to novelty when no expectation exists
    - NO reward
    - NO action selection
    - NO memory writes (Option A remains in close_frame)
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    # ---------------------------------
    # ENSURE ENGINES EXIST (SAFE)
    # ---------------------------------
    state.setdefault("preference_store", PreferenceStore())
    state.setdefault(
        "preference_engine",
        PreferenceEngine(
            store=state["preference_store"],
            cfg=PreferenceConfig(),
        ),
    )

    state.setdefault("expectation_store", ExpectationStore())
    state.setdefault(
        "expectation_engine",
        ExpectationEngine(store=state["expectation_store"]),
    )

    pref_engine: PreferenceEngine = state["preference_engine"]
    exp_engine: ExpectationEngine = state["expectation_engine"]

    frames = state["frames"]
    frame = frames.active

    # ---------------------------------
    # PERCEPTION
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

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # ---------------------------------
    # CONTEXT KEY (SHARED ACROSS SYSTEM)
    # ---------------------------------
    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        notes=percept_notes,
    )

    # ---------------------------------
    # OBSERVED VECTOR (Phase 7.1)
    # ---------------------------------
    observed = exp_engine.observed_vector(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    expected = exp_engine.store.get(context_key)

    # ---------------------------------
    # PREDICTION ERROR (Phase 7.2)
    # ---------------------------------
    if expected is None:
        # First exposure → novelty
        prediction_error = 0.25
        pe_reason = "novel"
    else:
        # L1 distance in expectation space
        prediction_error = (
            abs(observed.fragment_density - expected.fragment_density)
            + abs(observed.action_diversity - expected.action_diversity)
            + abs(observed.coherence - expected.coherence)
            + abs(observed.fragmentation - expected.fragmentation)
            + abs(observed.block_rate - expected.block_rate)
        ) / 5.0
        prediction_error = min(1.0, max(0.0, prediction_error))
        pe_reason = "expected_mismatch"

    state["prediction_error"] = float(prediction_error)

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # ---------------------------------
    # WRITE LAST_* CHANNELS (ATTENTION LOOP)
    # ---------------------------------
    state["last_coherence"] = coherence
    state["last_fragmentation"] = Z
    state["last_block_rate"] = block_rate
    state["last_percept_notes"] = list(percept_notes)

    # ---------------------------------
    # PREFERENCE UPDATE (READ-ONLY BIAS)
    # ---------------------------------
    pref_update = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
        prediction_error_l1=prediction_error,
    )

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": pref_update.context_key,
        "previous": pref_update.previous,
        "updated": pref_update.updated,
        "delta": pref_update.delta,
        "reason": pref_update.reason,
        "prediction_error": prediction_error,
        "pe_reason": pe_reason,
    }