# embodiment/local/candidates.py

from dataclasses import dataclass
from typing import FrozenSet, Tuple


@dataclass(frozen=True)
class LedgerCandidate:
    """
    A provisional embodied invariant.
    NOT truth. NOT knowledge.
    """
    kind: str
    regions: FrozenSet[str]
    conditions: Tuple[str, ...]
    support: int
    stability: float