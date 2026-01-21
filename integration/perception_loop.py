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
# CONSTANTS (SAFE, SMALL)
# --------------------------------------------------

BASE_ATTENTION: float = 1.0


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
    # PHASE 6.1 — ATTENTION (READ-ONLY BIAS)
    # --------------------------------------------------

    attention_gain: float = BASE_ATTENTION

    pref_store = state.get("preference_store")
    pref_engine = state.get("preference_engine")

    if pref_store and pref_engine:
        try:
            # Use LAST preference context only
            last_update = state.get("last_preference_update")

            if last_update:
                context_key = last_update.get("context")
                if context_key:
                    pref_score = float(pref_store.get(context_key))

                    attention_gain = compute_attention_gain(
                        preference_score=pref_score
                    )

        except Exception:
            # Perception must NEVER fail
            attention_gain = BASE_ATTENTION

    # --------------------------------------------------
    # CREATE FRAGMENT (IMMUTABLE)
    # --------------------------------------------------

    frag = Fragment(
        kind="contact",
        payload={
            **base_payload,
            "attention": float(attention_gain),  # STRUCTURAL, READ-ONLY
        },
    )

    fragments.append(frag)

    return fragments