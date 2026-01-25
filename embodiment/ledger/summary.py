# embodiment/ledger/summary.py

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet, Iterable

from embodiment.ledger.entry import LedgerEntry
from embodiment.ledger.ledger import EmbodimentLedger


# ============================================================
# Embodiment Summary Doctrine
#
# - Read-only
# - Structural only
# - No decisions
# - No confidence inflation
# - No gating
#
# This is the ONLY legal way embodiment is observed
# by higher-level systems.
# ============================================================


@dataclass(frozen=True)
class EmbodimentSummary:
    """
    Structural snapshot of embodied invariants.

    This is NOT knowledge.
    This is NOT belief.
    This is NOT memory.

    It is a statistical view of what has stabilized.
    """

    total_invariants: int

    boundary_regions: FrozenSet[str]
    thermal_regions: FrozenSet[str]
    pain_regions: FrozenSet[str]
    ownership_regions: FrozenSet[str]
    skill_regions: FrozenSet[str]

    avg_confidence: float
    avg_stability: float


# ============================================================
# Summary Builder
# ============================================================

def summarize_ledger(ledger: EmbodimentLedger) -> EmbodimentSummary:
    """
    Create a structural summary of the Embodiment Ledger.

    This function MUST:
    - be deterministic
    - be side-effect free
    - never filter or interpret semantics
    """

    entries: Iterable[LedgerEntry] = ledger.all_latest()

    boundaries = set()
    thermals = set()
    pains = set()
    ownerships = set()
    skills = set()

    total_confidence = 0.0
    total_stability = 0.0
    count = 0

    for entry in entries:
        count += 1
        total_confidence += entry.confidence
        total_stability += entry.stability

        if entry.kind == "boundary":
            boundaries.update(entry.regions)
        elif entry.kind == "thermal":
            thermals.update(entry.regions)
        elif entry.kind == "pain":
            pains.update(entry.regions)
        elif entry.kind == "ownership":
            ownerships.update(entry.regions)
        elif entry.kind == "skill":
            skills.update(entry.regions)

    avg_conf = total_confidence / count if count > 0 else 0.0
    avg_stab = total_stability / count if count > 0 else 0.0

    return EmbodimentSummary(
        total_invariants=count,
        boundary_regions=frozenset(boundaries),
        thermal_regions=frozenset(thermals),
        pain_regions=frozenset(pains),
        ownership_regions=frozenset(ownerships),
        skill_regions=frozenset(skills),
        avg_confidence=avg_conf,
        avg_stability=avg_stab,
    )