from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple, FrozenSet, Optional


# ============================================================
# Choice Doctrine
#
# A Choice is NOT:
# - a command
# - a goal
# - a reward
# - a preference
# - an act of will
#
# A Choice IS:
# - a post-hoc structural resolution
# - an acknowledgement that one outcome
#   reduced instability more reliably
#
# The system does not "choose".
# Choices are observed after settlement.
# ============================================================


@dataclass(frozen=True)
class ConsolidationChoice:
    """
    A recorded structural choice emerging from resolved experience.

    Choices do not cause behavior.
    They summarize what *worked* under constraints.
    """

    # identity
    kind: str
    regions: FrozenSet[str]

    # conditions under which the choice held
    conditions: Tuple[str, ...]

    # structural evidence
    support: int                  # number of resolved episodes
    stability: float              # [0..1] structural consistency
    confidence: float             # [0..1] slow-moving trust

    # bookkeeping
    version: int = 1
    source: str = "consolidation" # always post-frame


# ============================================================
# Choice Candidate (Pre-ledger)
# ============================================================

@dataclass(frozen=True)
class ChoiceCandidate:
    """
    A provisional choice awaiting consolidation.

    Created by the Accountant.
    Passed through the Consolidation Gate.
    """

    kind: str
    regions: FrozenSet[str]
    conditions: Tuple[str, ...]

    support: int
    stability: float
    confidence: float

    reason: str                   # why this candidate exists
    blocking: bool = False        # whether contradiction detected


# ============================================================
# Choice Revision
# ============================================================

def revise_choice(
    *,
    prior: ConsolidationChoice,
    added_support: int,
    stability_delta: float,
    confidence_delta: float,
) -> ConsolidationChoice:
    """
    Create a new version of an existing choice.

    History is preserved.
    Confidence changes are slow and bounded.
    """

    return ConsolidationChoice(
        kind=prior.kind,
        regions=prior.regions,
        conditions=prior.conditions,
        support=prior.support + added_support,
        stability=min(1.0, prior.stability + stability_delta),
        confidence=min(1.0, prior.confidence + confidence_delta),
        version=prior.version + 1,
        source=prior.source,
    )