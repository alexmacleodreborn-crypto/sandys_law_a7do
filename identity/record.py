from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List


@dataclass(frozen=True)
class IdentityRecord:
    """
    Identity = continuity substrate (NOT personality).

    Doctrine:
    - No time required
    - Anchored in body ownership + crystallized memory
    - Contains stable ids + small state variables only
    """

    identity_id: str
    genesis_id: str
    incarnation: int
    continuity_version: int

    # Structural continuity (bounded)
    stability_index: float      # [0..1] grows when coherence persists
    novelty_index: float        # [0..1] rises when prediction error persists
    embodiment_integrity: float # [0..1] rises when ownership signals are consistent

    # Commitments (non-semantic tags)
    commitments: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def clamp01(x: float) -> float:
        if x < 0.0:
            return 0.0
        if x > 1.0:
            return 1.0
        return float(x)