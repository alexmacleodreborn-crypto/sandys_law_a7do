# sandys_law_a7do/mind/regulation.py

from dataclasses import dataclass
from typing import Literal


Decision = Literal["allow", "slow", "pause"]


@dataclass(frozen=True)
class RegulationDecision:
    decision: Decision
    reason: str


def regulate(
    *,
    coherence: float,
    fragmentation: float,
    block_rate: float,
) -> RegulationDecision:
    """
    Internal self-regulation.

    This does NOT block actions globally.
    It emits a signal that gates or interfaces may respect later.
    """

    if block_rate > 0.8:
        return RegulationDecision("pause", "excessive_blocking")

    if fragmentation > 0.75:
        return RegulationDecision("slow", "high_fragmentation")

    if coherence < 0.3:
        return RegulationDecision("slow", "low_coherence")

    return RegulationDecision("allow", "stable")
