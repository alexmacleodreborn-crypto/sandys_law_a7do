# sandys_law_a7do/integration/perception_loop.py
"""
Phase 4.1 — Controlled Perceptual Diversity

Purpose:
- Introduce controlled structural diversity
- Allow Z to move without destabilising the system
- Preserve Sandy’s Law constraints

Important:
- This module must NOT depend on where PreferenceEngine lives.
- It reads bias from state only (if present).
"""

from __future__ import annotations

import random
from typing import List

from sandys_law_a7do.frames.fragment import Fragment


def perceive_and_act(state) -> List[Fragment]:
    """
    Minimal embodied perception loop.

    Produces small structural variation only.
    No semantics, no reward, no goals.

    Optional: if a preference engine exists in state, it may bias
    novelty probability very gently. No action selection.
    """

    fragments: List[Fragment] = []

    # --------------------------------------------------
    # Base environmental load (always present)
    # --------------------------------------------------
    load_level = random.choice(["low", "medium"])
    fragments.append(Fragment(kind=f"load:{load_level}"))

    # --------------------------------------------------
    # Preference-aware bias (READ-ONLY)
    # --------------------------------------------------
    # We don't import PreferenceEngine here; we only read from state.
    pref_engine = state.get("preference_engine", None)
    context_key = state.get("current_context_key", "none")

    # Default neutral bias
    bias = 0.0

    # If your PreferenceEngine has a store with prefs dict, use it safely.
    # (Works for both mind.preference and accounting.preference as long as
    # they expose .store.prefs)
    if pref_engine is not None:
        try:
            bias = float(getattr(getattr(pref_engine, "store", None), "prefs", {}).get(context_key, 0.0))
        except Exception:
            bias = 0.0

    # Map bias ∈ [-1, +1] → novelty probability adjustment ∈ [-0.08, +0.08]
    novelty_p = 0.30 + max(-0.08, min(0.08, 0.08 * bias))

    # --------------------------------------------------
    # Occasional novelty
    # --------------------------------------------------
    if random.random() < novelty_p:
        fragments.append(Fragment(kind="novel"))

    # --------------------------------------------------
    # Rare pressure spike (small chance)
    # --------------------------------------------------
    if random.random() < 0.10:
        fragments.append(Fragment(kind="pressure"))

    return fragments