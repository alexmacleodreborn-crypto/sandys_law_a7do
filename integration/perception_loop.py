"""
Perception Loop — Phase 6.2 (ATTENTION PERSISTENCE)

- Generates perceptual fragments
- Attention is READ-ONLY bias
- Attention has temporal inertia
- NO mutation of fragments
- NO memory writes
- NO action selection
"""

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


# ==================================================
# CONFIG (LOCKED)
# ==================================================

ATTENTION_ALPHA = 0.85      # persistence strength
ATTENTION_BASE = 1.0        # neutral baseline
ATTENTION_MIN = 0.5
ATTENTION_MAX = 1.5


# ==================================================
# MAIN LOOP
# ==================================================

def perceive_and_act(state: dict) -> List[Fragment]:
    fragments: List[Fragment] = []

    # ---------------------------------------------
    # Ensure attention state exists
    # ---------------------------------------------
    prev_attention = float(state.get("attention_level", ATTENTION_BASE))

    # ---------------------------------------------
    # Default attention (neutral)
    # ---------------------------------------------
    new_attention = ATTENTION_BASE

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

            new_attention = compute_attention_gain(
                preference_score=pref_score
            )

        except Exception:
            # Perception must NEVER fail
            new_attention = ATTENTION_BASE

    # ---------------------------------------------
    # Phase 6.2 — ATTENTION PERSISTENCE
    # ---------------------------------------------
    attention = (
        ATTENTION_ALPHA * prev_attention
        + (1.0 - ATTENTION_ALPHA) * new_attention
    )

    # Clamp (hard safety)
    attention = max(ATTENTION_MIN, min(ATTENTION_MAX, attention))

    # Store for next tick
    state["attention_level"] = attention

    # ---------------------------------------------
    # Emit fragment (IMMUTABLE)
    # ---------------------------------------------
    frag = Fragment(
        kind="contact",
        payload={
            "source": "demo",
            "attention": attention,
        },
    )

    fragments.append(frag)
    return fragments