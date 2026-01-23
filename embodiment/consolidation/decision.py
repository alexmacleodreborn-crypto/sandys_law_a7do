# embodiment/consolidation/decision.py

from __future__ import annotations
from dataclasses import dataclass
from typing import FrozenSet, Tuple, Optional


@dataclass(frozen=True)
class ConsolidationDecision:
    """
    A post-hoc structural resolution produced by the Consolidation Gate.

    A decision:
    - does NOT command behaviour
    - does NOT enforce rules
    - does NOT write memory directly
    - MAY result in ledger writing

    It exists to be:
    - inspected
    - audited
    - reasoned about later
    """

    # ----------------------------------
    # Identity
    # ----------------------------------
    decision_id: str
    kind: str                     # e.g. "embody", "defer", "reject"

    # ----------------------------------
    # Context
    # ----------------------------------
    candidate_kind: str            # boundary / thermal / pain / skill / ownership
    regions: FrozenSet[str]
    conditions: Tuple[str, ...]

    # ----------------------------------
    # Structural justification
    # ----------------------------------
    support: int
    stability: float
    confidence: float

    # ----------------------------------
    # Outcome
    # ----------------------------------
    ledger_write: bool
    reason: str

    # ----------------------------------
    # Versioning / traceability
    # ----------------------------------
    parent_version: Optional[int] = None