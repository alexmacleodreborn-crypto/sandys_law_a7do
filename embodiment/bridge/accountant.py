# embodiment/bridge/accountant.py

from __future__ import annotations
from typing import Dict

from embodiment.ledger.ledger import EmbodimentLedger


def summarize_embodiment(ledger: EmbodimentLedger) -> Dict[str, float]:
    """
    Read-only structural summary of embodied invariants.

    This function:
    - does NOT decide
    - does NOT gate
    - does NOT write memory
    - does NOT modify the ledger
    """

    entries = ledger.all_latest()

    if not entries:
        return {
            "embodied_count": 0,
            "avg_confidence": 0.0,
            "avg_stability": 0.0,
            "boundary_count": 0,
            "pain_count": 0,
            "ownership_count": 0,
        }

    confidence_sum = 0.0
    stability_sum = 0.0

    counts = {
        "boundary": 0,
        "pain": 0,
        "ownership": 0,
        "thermal": 0,
        "skill": 0,
    }

    for e in entries:
        confidence_sum += e.confidence
        stability_sum += e.stability
        counts[e.kind] = counts.get(e.kind, 0) + 1

    total = len(entries)

    return {
        "embodied_count": total,
        "avg_confidence": confidence_sum / total,
        "avg_stability": stability_sum / total,
        "boundary_count": counts.get("boundary", 0),
        "pain_count": counts.get("pain", 0),
        "ownership_count": counts.get("ownership", 0),
        "thermal_count": counts.get("thermal", 0),
        "skill_count": counts.get("skill", 0),
    }