from __future__ import annotations

from sandys_law_a7do.mind.perception import summarize_perception
from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

# NEW — embodiment candidate builder
from embodiment.local.candidates import CandidateBuilder


def step_tick(state, snapshot):
    """
    Phase 6.3 — Tick writes last_* structural channels

    - No reward
    - No action selection
    - No memory commit
    - Prebirth safe
    """

    # ---------------------------------
    # ADVANCE TIME
    # ---------------------------------
    state["ticks"] += 1

    # ---------------------------------
    # Preference engine (safe init)
    # ---------------------------------
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
    # STRUCTURAL PREDICTION ERROR
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
    # COHERENCE METRICS
    # ---------------------------------
    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)
    block_rate = float(report.block_rate)