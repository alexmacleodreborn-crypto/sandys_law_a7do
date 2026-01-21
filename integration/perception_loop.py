# sandys_law_a7do/integration/perception_loop.py
"""
Phase 7 (B) — Preference-biased Fragment Diversity (NO reward)

Purpose:
- Keep Sandy’s Law constraints: no goals, no reward, no semantics, no time
- Use *Preference* as a slow structural bias that alters *diversity* of produced fragments
- High preference -> fewer novel/pressure fragments, fewer action-kinds (settling)
- Low preference  -> more novel/pressure fragments, more action-kinds (diversifying)

This file ONLY generates fragments. It does not update memory, preferences, or choose goals.
"""

from __future__ import annotations

import random
from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.mind.coherence import compute_coherence

# PreferenceEngine is optional at runtime; we only use it if present in state.
try:
    from sandys_law_a7do.mind.preference import PreferenceEngine
except Exception:  # pragma: no cover
    PreferenceEngine = None  # type: ignore


def _clip(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(v)))


def _notes_from_frame_kinds(kinds: List[str]) -> List[str]:
    """
    Tiny, non-semantic notes used only to form a structural context key.
    """
    notes: List[str] = []

    if any(k.startswith("load:high") for k in kinds):
        notes.append("persistent_blocking")

    # "high_fragmentation" / "high_coherence" are coarse structural flags
    # (still not semantic).
    return notes


def _get_preference_bias(state) -> float:
    """
    Returns preference score in [-1, +1] for the *current structural context*.
    If preference engine doesn't exist yet, returns 0.0 (neutral).
    """
    engine = state.get("preference_engine", None)
    if engine is None or PreferenceEngine is None:
        return 0.0

    frames = state.get("frames")
    frame = getattr(frames, "active", None)
    if frame is None:
        return 0.0

    kinds = [f.kind for f in getattr(frame, "fragments", [])]
    fragment_count = len(kinds)
    unique_actions = len(set(kinds))

    report = compute_coherence(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        blocked_events=0,
    )

    coherence = float(report.coherence)
    fragmentation = float(report.fragmentation)
    block_rate = float(report.block_rate)

    notes = _notes_from_frame_kinds(kinds)

    # Build the same kind of structural key the PreferenceEngine uses
    # (bins only, no semantics).
    try:
        context_key = engine.context_key_from_accounting(
            coherence=coherence,
            fragmentation=fragmentation,
            block_rate=block_rate,
            notes=notes,
        )
    except Exception:
        return 0.0

    # Read current stored preference score for this context
    try:
        score = engine.store.get(context_key)
        return float(_clip(score, -1.0, 1.0))
    except Exception:
        return 0.0


def perceive_and_act(state) -> List[Fragment]:
    """
    Phase 7(B): produce fragments with preference-biased diversity.

    Output fragments are still structural labels only:
      - load:* (environmental load proxy)
      - act:*  (non-semantic action-kinds)
      - novel  (novelty marker)
      - pressure (spike marker)
    """
    pref = _get_preference_bias(state)  # [-1..+1]

    # ------------------------------
    # Base probabilities (Phase 4.1)
    # ------------------------------
    base_novel_p = 0.30
    base_pressure_p = 0.10

    # ------------------------------
    # Bias rules:
    #  pref > 0  => settle (less novelty/pressure, fewer action kinds)
    #  pref < 0  => diversify (more novelty/pressure, more action kinds)
    # ------------------------------
    # Map pref into multipliers:
    # +1 => 0.4x novelty, 0.5x pressure
    # -1 => 1.6x novelty, 1.8x pressure
    novelty_mult = _clip(1.0 - 0.6 * pref, 0.4, 1.6)
    pressure_mult = _clip(1.0 - 0.8 * pref, 0.5, 1.8)

    novel_p = _clip(base_novel_p * novelty_mult, 0.02, 0.85)
    pressure_p = _clip(base_pressure_p * pressure_mult, 0.01, 0.65)

    # Action diversity: how many different "act:*" kinds we emit per call
    # +1 => 1 action, 0 => 1-2 actions, -1 => 2-3 actions
    if pref >= 0.6:
        n_actions = 1
    elif pref <= -0.6:
        n_actions = 3
    else:
        n_actions = random.choice([1, 2])

    # ------------------------------
    # Build fragments
    # ------------------------------
    fragments: List[Fragment] = []

    # Environmental load proxy
    # pref high => more "low"
    # pref low  => allow "medium"/"high" more often
    load_roll = random.random()
    if pref >= 0.5:
        load_level = "low" if load_roll < 0.80 else "medium"
    elif pref <= -0.5:
        load_level = "high" if load_roll < 0.35 else ("medium" if load_roll < 0.75 else "low")
    else:
        load_level = "low" if load_roll < 0.55 else "medium"

    fragments.append(Fragment(kind=f"load:{load_level}"))

    # Non-semantic action-kinds (structural diversity only)
    action_pool = [
        "act:probe",
        "act:orient",
        "act:hold",
        "act:step",
        "act:scan",
    ]
    chosen = random.sample(action_pool, k=min(n_actions, len(action_pool)))
    for a in chosen:
        fragments.append(Fragment(kind=a))

    # Novelty + pressure markers
    if random.random() < novel_p:
        fragments.append(Fragment(kind="novel"))

    if random.random() < pressure_p:
        fragments.append(Fragment(kind="pressure"))

    return fragments