from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, FrozenSet


# ============================================================
# Candidate Doctrine
#
# A candidate is:
# - provisional
# - structural
# - conservative
# - local-first
#
# Candidates do NOT:
# - assert truth
# - modify embodiment ledger
# - bypass consolidation
#
# Candidates EXIST to say:
# "This keeps happening under these conditions."
# ============================================================


# ------------------------------------------------------------
# Embodiment Candidate
# ------------------------------------------------------------

@dataclass(frozen=True)
class EmbodimentCandidate:
    """
    A proposed embodied invariant awaiting consolidation.
    """

    kind: str                        # "boundary", "thermal", "pain", "skill", "ownership"
    regions: FrozenSet[str]

    conditions: FrozenSet[str]       # symbolic labels only
    support: int                     # number of supporting episodes

    stability: float                 # [0..1]
    confidence_hint: float           # conservative upper bound


# ------------------------------------------------------------
# Candidate Builder
# ------------------------------------------------------------

class CandidateBuilder:
    """
    Builds embodiment candidates from local structural state.

    Inputs:
    - coupling snapshot
    - reflex history summaries (optional, passed externally)

    Output:
    - list of EmbodimentCandidate
    """

    # Conservative thresholds
    PAIN_THRESHOLD = 0.6
    LOAD_THRESHOLD = 0.7
    STABILITY_THRESHOLD = 0.65

    def __init__(self) -> None:
        pass

    # --------------------------------------------------------
    # Main API
    # --------------------------------------------------------

    def build_from_coupling(
        self,
        *,
        snapshot: Dict[str, Dict[str, float]],
        support: int,
    ) -> List[EmbodimentCandidate]:
        """
        Convert coupling snapshot into candidate invariants.

        snapshot:
            {
              region: {
                "load": float,
                "pain": float,
                "stability": float
              }
            }
        """

        candidates: List[EmbodimentCandidate] = []

        for region, values in snapshot.items():
            pain = values.get("pain", 0.0)
            load = values.get("load", 0.0)
            stability = values.get("stability", 1.0)

            # --------------------------------------------
            # Pain Surface Candidate
            # --------------------------------------------
            if pain >= self.PAIN_THRESHOLD:
                candidates.append(
                    EmbodimentCandidate(
                        kind="pain",
                        regions=frozenset({region}),
                        conditions=frozenset({"contact", "overload"}),
                        support=support,
                        stability=max(0.0, 1.0 - pain),
                        confidence_hint=min(0.6, pain),
                    )
                )

            # --------------------------------------------
            # Boundary Candidate
            # --------------------------------------------
            if load >= self.LOAD_THRESHOLD and stability < self.STABILITY_THRESHOLD:
                candidates.append(
                    EmbodimentCandidate(
                        kind="boundary",
                        regions=frozenset({region}),
                        conditions=frozenset({"pressure", "blocked_motion"}),
                        support=support,
                        stability=stability,
                        confidence_hint=0.5,
                    )
                )

            # --------------------------------------------
            # Ownership Candidate
            # --------------------------------------------
            if stability >= 0.8 and load < 0.4 and pain < 0.3:
                candidates.append(
                    EmbodimentCandidate(
                        kind="ownership",
                        regions=frozenset({region}),
                        conditions=frozenset({"responsive", "controllable"}),
                        support=support,
                        stability=stability,
                        confidence_hint=0.4,
                    )
                )

        return candidates