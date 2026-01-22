# embodiment/ledger/entry.py

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, FrozenSet


@dataclass(frozen=True)
class LedgerEntry:
    """
    A grounded embodied invariant.

    This represents something that has remained stable across
    repeated lived experience under constrained conditions.

    Ledger entries are:
    - conditional
    - conservative
    - versioned
    - grounded in interaction
    """

    # identity
    kind: str                     # e.g. "boundary", "thermal", "pain", "skill", "ownership"
    regions: FrozenSet[str]       # body or surface regions involved

    # conditions
    conditions: Tuple[str, ...]   # symbolic constraints (NOT logic)

    # support
    support: int                  # number of supporting episodes
    stability: float              # [0..1] structural stability

    # confidence
    confidence: float             # derived, monotonic, slow-changing

    # versioning
    version: int = 1

    def revise(
        self,
        *,
        added_support: int,
        stability_delta: float,
        confidence_delta: float,
    ) -> "LedgerEntry":
        """
        Create a revised version of this entry.
        Revisions never overwrite history.
        """
        return LedgerEntry(
            kind=self.kind,
            regions=self.regions,
            conditions=self.conditions,
            support=self.support + added_support,
            stability=min(1.0, self.stability + stability_delta),
            confidence=min(1.0, self.confidence + confidence_delta),
            version=self.version + 1,
        )