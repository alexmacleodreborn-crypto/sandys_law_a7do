# embodiment/ledger/summary.py

from __future__ import annotations
from typing import Dict

from embodiment.ledger.entry import LedgerEntry
from embodiment.ledger.ledger import EmbodimentLedger


# ============================================================
# Embodiment Summary Doctrine
#
# - READ-ONLY
# - STRUCTURAL ONLY
# - NO SEMANTICS
# - NO DECISIONS
#
# This summary exists ONLY to expose:
#   - how much embodiment exists
#   - how stable it is
#   - how confident it is
#
# It is SAFE to pass upward to the Accountant.
# ============================================================


def summarize_ledger(ledger: EmbodimentLedger) -> Dict[str, float | int]:
    """
    Produce a structural summary of the embodiment ledger.

    This function:
    - does NOT modify the ledger
    - does NOT infer meaning
    - does NOT create confidence
    """

    entries = ledger.latest_all()

    if not entries:
        return {
            "count": 0,
            "mean_stability": 0.0,
            "mean_confidence": 0.0,
            "max_version": 0,
        }

    count = len(entries)
    mean_stability = sum(e.stability for e in entries) / count
    mean_confidence = sum(e.confidence for e in entries) / count
    max_version = max(e.version for e in entries)

    return {
        "count": count,
        "mean_stability": float(mean_stability),
        "mean_confidence": float(mean_confidence),
        "max_version": int(max_version),
    }