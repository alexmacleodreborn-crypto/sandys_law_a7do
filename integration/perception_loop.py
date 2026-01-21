# sandys_law_a7do/integration/perception_loop.py
"""
Perception Loop — Phase 6.1 (IMMUTABLE SAFE)

Responsibilities:
- Generate perceptual fragments (small structural diversity)
- Carry READ-ONLY attention as structural payload
- NO mutation of Fragment instances
- NO action selection
- NO memory writes
"""

from __future__ import annotations

import random
from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


def _clip01(v: float) -> float:
    v = float(v)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def perceive_and_act(state: dict) -> List[Fragment]:
    """
    Phase 4–6 perception loop.

    Generates fragments and embeds attention
    as STRUCTURAL PAYLOAD (immutable-safe).

    Attention is computed from preference context (if available),
    else defaults to neutral base.
    """

    fragments: List[Fragment] = []

    # ---------------------------
    # Default attention (neutral)
    # ---------------------------
    attention_gain = 0.50

    pref_store = state.get("preference_store")
    pref_engine = state.get("preference_engine")

    if pref_store and pref_engine:
        try:
            coherence = float(state.get("last_coherence", 0.0))
            fragmentation = float(state.get("last_fragmentation", 0.0))
            block_rate = float(state.get("last_block_rate", 0.0))
            notes = state.get("last_percept_notes", [])

            context_key = pref_engine.context_key_from_accounting(
                coherence=coherence,
                fragmentation=fragmentation,
                block_rate=block_rate,
                notes=notes,
            )

            pref_score = float(pref_store.get(context_key))  # [-1..+1]
            attention_gain = compute_attention_gain(preference_score=pref_score)

        except Exception:
            attention_gain = 0.50

    # Defensive clip (never allow >1)
    attention_gain = _clip01(attention_gain)

    # --------------------------------------------------
    # Controlled structural diversity (keeps Z moving)
    # --------------------------------------------------
    # Always a base "contact"
    fragments.append(
        Fragment(
            kind="contact",
            payload={"source": "demo", "attention": attention_gain},
        )
    )

    # Occasional novelty (30%)
    if random.random() < 0.30:
        fragments.append(
            Fragment(
                kind="novel",
                payload={"source": "demo", "attention": attention_gain},
            )
        )

    # Rare pressure (10%)
    if random.random() < 0.10:
        fragments.append(
            Fragment(
                kind="pressure",
                payload={"source": "demo", "attention": attention_gain},
            )
        )

    return fragments