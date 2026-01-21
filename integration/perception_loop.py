# sandys_law_a7do/integration/perception_loop.py
"""
Perception Loop — Phase 6.1 (IMMUTABLE SAFE)

Responsibilities:
- Generate perceptual fragments
- Carry READ-ONLY attention as structural payload
- NO mutation of Fragment instances
- NO action selection
- NO memory writes
"""

from __future__ import annotations

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


def perceive_and_act(state: dict) -> List[Fragment]:
    """
    Phase 4–6 perception loop.

    Generates fragments and embeds attention
    as STRUCTURAL PAYLOAD (immutable-safe).
    """

    fragments: List[Fragment] = []

    # --------------------------------------------------
    # BASE PERCEPTION (DEMO / PLACEHOLDER)
    # --------------------------------------------------
    base_payload = {"source": "demo"}

    # --------------------------------------------------
    # PHASE 6.1 — ATTENTION (READ-ONLY)
    # --------------------------------------------------
    # Keep bounded and stable. Baseline attention is 1.0.
    base_attention = 1.0

    # Small bias multiplier so preference never explodes attention.
    # compute_attention_gain should also be bounded, but we clamp anyway.
    attention_gain = base_attention

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

            pref_score = float(pref_store.get(context_key))

            # Convert preference score -> attention gain (read-only bias)
            attention_gain = float(
                compute_attention_gain(preference_score=pref_score)
            )

        except Exception:
            # Perception must NEVER fail
            attention_gain = base_attention

    # Hard clamp (prevents “1 then jumps to 1.5” runaway, keeps graphs sane)
    if attention_gain < 0.5:
        attention_gain = 0.5
    if attention_gain > 1.5:
        attention_gain = 1.5

    # --------------------------------------------------
    # CREATE FRAGMENT (IMMUTABLE)
    # --------------------------------------------------
    frag = Fragment(
        kind="contact",
        payload={
            **base_payload,
            "attention": attention_gain,  # ✅ structural, immutable-safe
        },
    )

    fragments.append(frag)
    return fragments