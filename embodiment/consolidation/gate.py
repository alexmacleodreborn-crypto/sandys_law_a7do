from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable

from embodiment.ledger.entry import LedgerEntry
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.local.candidates import EmbodimentCandidate


# ============================================================
# Consolidation Decision
# ============================================================

@dataclass(frozen=True)
class ConsolidationDecision:
    """
    Result of consolidation evaluation.
    """
    action: str                  # "accept", "revise", "defer"
    reason: str
    entry: Optional[LedgerEntry]


# ============================================================
# Consolidation Gate
# ============================================================

class ConsolidationGate:
    """
    The sole authority for writing embodied invariants.

    This gate is:
    - conservative
    - evidence-based
    - structure-preserving
    - side-effect minimal
    """

    # ---------------------------------
    # Thresholds (v1, conservative)
    # ---------------------------------
    MIN_SUPPORT = 5
    MIN_STABILITY = 0.65
    MIN_CONFIDENCE = 0.5

    MAX_CONFIDENCE_STEP = 0.1
    MAX_STABILITY_STEP = 0.1

    # ---------------------------------
    # Main evaluation
    # ---------------------------------

    def evaluate(
        self,
        *,
        candidate: EmbodimentCandidate,
        ledger: EmbodimentLedger,
    ) -> ConsolidationDecision:
        """
        Evaluate a candidate for embodiment consolidation.

        This function is deterministic and auditable.
        """

        # Rule 1: insufficient evidence
        if candidate.support < self.MIN_SUPPORT:
            return self._defer("insufficient_support")

        if candidate.stability < self.MIN_STABILITY:
            return self._defer("insufficient_stability")

        # Rule 2: locate existing entry (if any)
        existing = ledger.find_matching(
            kind=candidate.kind,
            regions=candidate.regions,
            conditions=candidate.conditions,
        )

        if existing is None:
            return self._accept_new(candidate)

        # Rule 3: revision path
        return self._revise_existing(candidate, existing)

    # --------------------------------------------------------
    # Accept new invariant
    # --------------------------------------------------------

    def _accept_new(
        self,
        candidate: EmbodimentCandidate,
    ) -> ConsolidationDecision:
        entry = LedgerEntry(
            kind=candidate.kind,
            regions=candidate.regions,
            conditions=candidate.conditions,
            support=candidate.support,
            stability=min(1.0, candidate.stability),
            confidence=min(1.0, candidate.confidence),
            version=1,
        )

        return ConsolidationDecision(
            action="accept",
            reason="new_invariant_stable",
            entry=entry,
        )

    # --------------------------------------------------------
    # Revise existing invariant
    # --------------------------------------------------------

    def _revise_existing(
        self,
        candidate: EmbodimentCandidate,
        existing: LedgerEntry,
    ) -> ConsolidationDecision:
        revised = existing.revise(
            added_support=candidate.support,
            stability_delta=min(
                self.MAX_STABILITY_STEP,
                candidate.stability - existing.stability,
            ),
            confidence_delta=min(
                self.MAX_CONFIDENCE_STEP,
                candidate.confidence - existing.confidence,
            ),
        )

        return ConsolidationDecision(
            action="revise",
            reason="consistent_with_existing_invariant",
            entry=revised,
        )

    # --------------------------------------------------------
    # Defer utility
    # --------------------------------------------------------

    @staticmethod
    def _defer(reason: str) -> ConsolidationDecision:
        return ConsolidationDecision(
            action="defer",
            reason=reason,
            entry=None,
        )