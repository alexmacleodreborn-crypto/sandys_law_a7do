from __future__ import annotations

from sandys_law_a7do.bootstrap import tick_system

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)


# ============================================================
# ATTENTION DECAY CONSTANTS
# ============================================================
ATTENTION_DECAY = 0.97        # slow evening
ATTENTION_MIN = 0.2           # biological floor


def step_tick(state, snapshot):
    """
    Phase 7.4 — Cognitive Tick (Clock Delegated)

    - Time advancement delegated to bootstrap.tick_system
    - Womb physics stepped BEFORE cognition
    - No action selection
    - No reward
    - No semantic memory
    """

    # =========================================================
    # AUTHORITATIVE TIME + WOMB STEP
    # =========================================================
    tick_system(state)

    # =========================================================
    # ENSURE PREFERENCE ENGINE EXISTS (SAFE)
    # =========================================================
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

    # =========================================================
    # PERCEPTION
    # =========================================================
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

    # =========================================================
    # STRUCTURAL PREDICTION ERROR
    # =========================================================
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

    # =========================================================
    # STRUCTURAL METRICS
    # =========================================================
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

    # =========================================================
    # REGULATION (READ-ONLY)
    # =========================================================
    regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=block_rate,
    )

    # =========================================================
    # WRITE STRUCTURAL CHANNELS
    # =========================================================
    state["last_coherence"] = float(coherence)
    state["last_fragmentation"] = float(Z)
    state["last_block_rate"] = float(block_rate)
    state["last_percept_notes"] = list(percept_notes)

    # =========================================================
    # PREFERENCE UPDATE (STRUCTURAL BIAS ONLY)
    # =========================================================
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

    # =========================================================
    # ATTENTION SURFACE CHANNEL (WITH EVENING / DECAY)
    # =========================================================
    previous_attention = float(state.get("last_attention", 1.0))

    if frame and frame.fragments:
        last_frag = frame.fragments[-1]
        try:
            # reinforcement from stimulus
            attention = float(last_frag.payload.get("attention", previous_attention))
        except Exception:
            attention = previous_attention
    else:
        # evening / decay when no stimulus
        attention = previous_attention * ATTENTION_DECAY

    # enforce biological floor
    state["last_attention"] = max(ATTENTION_MIN, float(attention))