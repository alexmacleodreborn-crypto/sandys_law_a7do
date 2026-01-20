# sandys_law_a7do/scuttling/load_reduction.py

from dataclasses import dataclass
from typing import Literal


ReductionType = Literal["none", "simplify", "halt"]


@dataclass(frozen=True)
class LoadReductionDecision:
    """
    Decision to reduce motor complexity under load.
    """
    reduction: ReductionType
    reason: str


def decide_load_reduction(
    *,
    load: float,
    stability: float,
) -> LoadReductionDecision:
    """
    Determines whether motor complexity should be reduced.
    """
    if load > 0.85:
        return LoadReductionDecision("halt", "overload")

    if load > 0.6 or stability < 0.4:
        return LoadReductionDecision("simplify", "instability_or_load")

    return LoadReductionDecision("none", "stable")
