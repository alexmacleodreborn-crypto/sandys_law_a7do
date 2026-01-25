# embodiment/consolidation/gate.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from embodiment.ledger.entry import LedgerEntry
from embodiment.ledger.ledger import EmbodimentLedger


# ============================================================
# Consolidation Decision
# ============================================================

@dataclass(frozen=True)
class ConsolidationDecision:
    """
    Outcome of a consolidation attempt.
    """
    accepted: bool
    reason: str
    revised_entry: Optional[LedgerEntry] = None


# ============================================================
# Consolidation Gate
#
# This is the ONLY component allowed to write to the Ledger.
# ============================================================

class ConsolidationGate:
    """
    Conservative gate for embodied invariants.

    Properties:
    - deterministic
    - conservative
    - monotonic (confidence/support only increase)
    """

    # ----------------------------
    # Thresholds (v1 — strict)
    # ----------------------------
    MIN_SUPPORT = 3
    MIN_STABILITY = 0.6
    MIN_CONFIDENCE = 0.5

    # ----------------------------
    # Public API
    # ----------------------------

    def evaluate(
        self,
        *,
        candidate: LedgerEntry,
        ledger: EmbodimentLedger,
    ) -> ConsolidationDecision:
        """
        Decide whether a candidate invariant may be consolidated.
        """

        key = ledger._key(candidate)
        current = ledger.latest(key)

        # ----------------------------
        # First appearance
        # ----------------------------
        if current is None:
            if not self._meets_minimums(candidate):
                return ConsolidationDecision(
                    accepted=False,
                    reason="insufficient_initial_support",
                )

            ledger.add(candidate)
            return ConsolidationDecision(
                accepted=True,
                reason="new_invariant",
                revised_entry=candidate,
            )

        # ----------------------------
        # Revision of existing invariant
        # ----------------------------
        if not self._consistent(candidate, current):
            return ConsolidationDecision(
                accepted=False,
                reason="contradicts_existing_invariant",
            )

        revised = current.revise(
            added_support=candidate.support,
            stability_delta=candidate.stability - current.stability,
            confidence_delta=candidate.confidence - current.confidence,
        )

        ledger.add(revised)
        return ConsolidationDecision(
            accepted=True,
            reason="invariant_revised",
            revised_entry=revised,
        )

    # --------------------------------------------------------
    # Internal checks
    # --------------------------------------------------------

    def _meets_minimums(self, entry: LedgerEntry) -> bool:
        return (
            entry.support >= self.MIN_SUPPORT
            and entry.stability >= self.MIN_STABILITY
            and entry.confidence >= self.MIN_CONFIDENCE
        )

    def _consistent(self, new: LedgerEntry, old: LedgerEntry) -> bool:
        """
        Conservative consistency check.
        """
        if new.kind != old.kind:
            return False
        if new.regions != old.regions:
            return False
        if new.conditions != old.conditions:
            return False
        return True