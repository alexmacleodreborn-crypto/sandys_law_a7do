"""
Perception Loop — Phase 6.1 (IMMUTABLE SAFE)

- Generates perceptual fragments
- Embeds attention as STRUCTURAL PAYLOAD
- No mutation
- No memory
- No actions
"""

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


def perceive_and_act(state: dict) -> List[Fragment]:
    fragments: List[Fragment] = []

    base_attention = 0.5
    preference_bias = 1.0
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
            attention_gain = compute_attention_gain(preference_score=pref_score)

        except Exception:
            attention_gain = base_attention

    frag = Fragment(
        kind="contact",
        payload={
            "source": "demo",
            "attention": float(attention_gain),
        },
    )

    fragments.append(frag)
    return fragments