# sandys_law_a7do/accounting/attention.py
"""
Attention Gain — Phase 6.x (BOUNDED)

Attention is a structural scalar in [0..1].
It is NOT reward, NOT value, NOT action selection.

Inputs:
- preference_score in [-1..+1] (stored bias toward stability)

Output:
- attention_gain in [0..1]
"""

from __future__ import annotations


def _clip01(v: float) -> float:
    v = float(v)
    if v < 0.0:
        return 0.0
    if v > 1.0:
        return 1.0
    return v


def compute_attention_gain(
    *,
    preference_score: float,
    base: float = 0.50,
    span: float = 0.45,
) -> float:
    """
    Map preference_score [-1..+1] -> attention [0..1].

    - base is the default attention when preference is neutral
    - span is how much preference can move attention up/down
    """
    # Ensure preference is in [-1..+1]
    ps = float(preference_score)
    if ps < -1.0:
        ps = -1.0
    if ps > 1.0:
        ps = 1.0

    # Linear bounded map:
    # ps=-1 -> base - span
    # ps= 0 -> base
    # ps=+1 -> base + span
    gain = float(base) + float(span) * ps
    return _clip01(gain)