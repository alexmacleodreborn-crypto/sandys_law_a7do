import random
from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.preference_field import AttentionField
from sandys_law_a7do.accounting.preference import PreferenceEngine


def perceive_and_act(state) -> List[Fragment]:
    """
    Phase 5.3 — Attention-biased perception.

    - NO action selection
    - NO reward
    - NO goals
    - NO semantics
    """

    pref_engine: PreferenceEngine | None = state.get("preference_engine")

    attention = AttentionField(
        weights=pref_engine.attention_field() if pref_engine else {}
    )

    fragments: List[Fragment] = []

    # Structural context already computed upstream
    context_key = state.get("current_context_key", "none")

    attn = attention.get(context_key)

    # Gentle probabilistic salience
    if random.random() <= min(1.0, attn):
        fragments.append(
            Fragment(kind=random.choice(["contact", "force", "thermal"]))
        )

    return fragments