# sandys_law_a7do/integration/perception_loop.py
"""
Perception Loop — Phase 6.2 (IMMUTABLE SAFE)

Responsibilities:
- Generate perceptual fragments continuously
- Embed READ-ONLY attention as payload (no mutation of Fragment)
- NO memory writes
- NO action selection
- NEVER throw (perception must not crash the app)
"""

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


def perceive_and_act(state: dict) -> List[Fragment]:
    fragments: List[Fragment] = []

    base_attention = 1.0
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

            attention_gain = float(
                compute_attention_gain(preference_score=pref_score)
            )
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