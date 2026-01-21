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

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


# --------------------------------------------------
# MAIN PERCEPTION LOOP
# --------------------------------------------------

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

    attention_gain = base_attention * preference_bias

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

            pref_score = pref_store.get(context_key)

            attention_gain = compute_attention_gain(
                preference_score=pref_score
            )

        except Exception:
            # Perception must NEVER fail
            attention_gain = base_attention * preference_bias

    # --------------------------------------------------
    # CREATE FRAGMENT (IMMUTABLE)
    # --------------------------------------------------

    frag = Fragment(
        kind="contact",
        payload={
            **base_payload,
            "attention": attention_gain,  # ✅ STRUCTURAL, IMMUTABLE
        },
    )

    fragments.append(frag)

    return fragments