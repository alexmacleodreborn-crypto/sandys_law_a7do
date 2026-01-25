from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, FrozenSet

from embodiment.ledger.invariants import EmbodimentKind


@dataclass(frozen=True)
class LedgerEntry:
    """
    A grounded embodied invariant.
    """

    kind: EmbodimentKind
    regions: FrozenSet[str]
    conditions: Tuple[str, ...]

    support: int
    stability: float
    confidence: float

    version: int = 1

    def revise(
        self,
        *,
        added_support: int,
        stability_delta: float,
        confidence_delta: float,
    ) -> "LedgerEntry":
        return LedgerEntry(
            kind=self.kind,
            regions=self.regions,
            conditions=self.conditions,
            support=self.support + added_support,
            stability=min(1.0, self.stability + stability_delta),
            confidence=min(1.0, self.confidence + confidence_delta),
            version=self.version + 1,
        )