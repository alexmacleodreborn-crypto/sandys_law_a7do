# sandys_law_a7do/accounting/attention.py

from typing import Optional


def compute_attention_gain(
    *,
    preference_score: Optional[float],
    base: float = 1.0,
    strength: float = 0.5,
    min_gain: float = 0.5,
    max_gain: float = 1.5,
) -> float:
    """
    Phase 6.1 — Preference-weighted attention (READ-ONLY)

    Maps preference score ∈ [-1, +1] into a soft attention gain.

    - No filtering
    - No decisions
    - No reward
    - No persistence

    gain = base + strength * preference_score
    """

    if preference_score is None:
        return base

    gain = base + strength * float(preference_score)

    if gain < min_gain:
        return min_gain
    if gain > max_gain:
        return max_gain
    return gain