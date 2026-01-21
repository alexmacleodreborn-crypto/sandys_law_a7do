# sandys_law_a7do/engine/tick_engine.py

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.preference import PreferenceEngine, PreferenceStore, PreferenceConfig


def step_tick(state, snapshot):
    """
    Phase 6.3 — Tick writes last_* structural channels (for attention loop)

    - No reward
    - No action selection
    - No memory commit here (Option A stays in close_frame)
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    # Ensure preference engine/store exist (safe)
    if "preference_store" not in state:
        state["preference_store"] = PreferenceStore()
    if "preference_engine" not in state:
        state["preference_engine"] = PreferenceEngine(
            store=state["preference_store"],
            cfg=PreferenceConfig(),
        )

    pref_engine: PreferenceEngine = state["preference_engine"]

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
    # STRUCTURAL PREDICTION ERROR (L1 proxy)
    # ---------------------------------
    last = state.get("last_percept")
    if last:
        pe_frag = abs(fragment_count - last.get("fragment_count", 0))
        pe_act = abs(unique_actions - last.get("unique_actions", 0))
        prediction_error = min(1.0, (pe_frag + pe_act) / 6.0)
    else:
        prediction_error = 0.25

    state["last_percept"] = {
        "fragment_count": fragment_count,
        "unique_actions": unique_actions,
        "notes": percept_notes,
    }
    state["prediction_error"] = float(prediction_error)

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

    # IMPORTANT: your bootstrap snapshot uses structural_load for stability.
    # Tick doesn't override that; it only records last_* channels used by attention.
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # ---------------------------------
    # REGULATION (READ-ONLY)
    # ---------------------------------
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # ---------------------------------
    # Phase 6.3 — WRITE LAST_* CHANNELS FOR ATTENTION LOOP
    # ---------------------------------
    state["last_coherence"] = float(coherence)
    state["last_fragmentation"] = float(Z)
    state["last_block_rate"] = float(block_rate)
    state["last_percept_notes"] = list(percept_notes)

    # ---------------------------------
    # PREFERENCE UPDATE (READ-ONLY BIAS)
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

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": pref_update.context_key,
        "previous": pref_update.previous,
        "updated": pref_update.updated,
        "delta": pref_update.delta,
        "reason": pref_update.reason,
        "prediction_error": float(prediction_error),
    }