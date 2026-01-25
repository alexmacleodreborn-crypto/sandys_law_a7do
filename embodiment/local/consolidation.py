# embodiment/consolidation/gate.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Iterable

from embodiment.ledger.entry import LedgerEntry
from embodiment.local.candidates import EmbodimentCandidate


# ============================================================
# Consolidation Gate Doctrine
#
# - This gate is the ONLY writer to the Embodiment Ledger
# - It does NOT infer, guess, or reason
# - It does NOT react to single episodes
# - It is conservative by default
#
# The gate answers ONE question only:
#   "Has this invariant become stable enough to exist?"
# ============================================================


@dataclass
class ConsolidationDecision:
    """
    Result of consolidation evaluation.
    """
    accepted: bool
    revised_entry: Optional[LedgerEntry]
    reason: str


class ConsolidationGate:
    """
    Structural consolidation engine.

    Input:
      - EmbodimentCandidate
      - Optional existing LedgerEntry

    Output:
      - ConsolidationDecision
    """

    # --------------------------------------------------------
    # Conservative thresholds (Phase 1)
    # --------------------------------------------------------
    MIN_SUPPORT = 3                 # number of episodes
    MIN_STABILITY = 0.65
    MIN_CONFIDENCE = 0.6

    MAX_STABILITY_STEP = 0.15       # per revision
    MAX_CONFIDENCE_STEP = 0.1

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        candidate: EmbodimentCandidate,
        existing: Optional[LedgerEntry] = None,
    ) -> ConsolidationDecision:
        """
        Evaluate whether a candidate may:
        - create a new ledger entry
        - revise an existing entry
        - or be rejected
        """

        # --------------------------------------------
        # Hard rejections (structural safety)
        # --------------------------------------------
        if candidate.support < self.MIN_SUPPORT:
            return self._reject("insufficient_support")

        if candidate.stability < self.MIN_STABILITY:
            return self._reject("insufficient_stability")

        if candidate.confidence < self.MIN_CONFIDENCE:
            return self._reject("insufficient_confidence")

        # --------------------------------------------
        # New entry
        # --------------------------------------------
        if existing is None:
            entry = LedgerEntry(
                kind=candidate.kind,
                regions=frozenset(candidate.regions),
                conditions=tuple(candidate.conditions),
                support=candidate.support,
                stability=candidate.stability,
                confidence=candidate.confidence,
                version=1,
            )

            return ConsolidationDecision(
                accepted=True,
                revised_entry=entry,
                reason="new_embodied_invariant",
            )

        # --------------------------------------------
        # Revision path
        # --------------------------------------------
        if not self._compatible(candidate, existing):
            return self._reject("incompatible_with_existing")

        revised = existing.revise(
            added_support=candidate.support,
            stability_delta=self._bounded_delta(
                candidate.stability - existing.stability,
                self.MAX_STABILITY_STEP,
            ),
            confidence_delta=self._bounded_delta(
                candidate.confidence - existing.confidence,
                self.MAX_CONFIDENCE_STEP,
            ),
        )

        return ConsolidationDecision(
            accepted=True,
            revised_entry=revised,
            reason="embodied_revision",
        )

    # --------------------------------------------------------
    # Compatibility
    # --------------------------------------------------------

    @staticmethod
    def _compatible(
        candidate: EmbodimentCandidate,
        entry: LedgerEntry,
    ) -> bool:
        """
        Conservative compatibility check.
        """
        if candidate.kind != entry.kind:
            return False

        if not set(candidate.regions).issubset(entry.regions):
            return False

        if set(candidate.conditions) != set(entry.conditions):
            return False

        return True

    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    @staticmethod
    def _bounded_delta(delta: float, max_step: float) -> float:
        if delta <= 0.0:
            return 0.0
        return min(delta, max_step)

    @staticmethod
    def _reject(reason: str) -> ConsolidationDecision:
        return ConsolidationDecision(
            accepted=False,
            revised_entry=None,
            reason=reason,
        )