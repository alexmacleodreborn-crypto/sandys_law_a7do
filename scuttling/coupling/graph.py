from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set, Iterable

from .region import CoupledRegion


@dataclass
class CouplingGraph:
    """
    Structural coupling topology for embodied scuttling.

    Doctrine:
    - Purely physical
    - No symbols
    - No memory
    - No decisions
    - No gates

    Purpose:
    - Allow load / recovery to propagate implicitly
    - Provide a stable snapshot for embodiment candidate extraction
    """

    regions: Dict[str, CoupledRegion] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)

    # =========================================================
    # REGION MANAGEMENT
    # =========================================================

    def add_region(self, region: CoupledRegion) -> None:
        """
        Register a new embodied region.
        """
        self.regions[region.name] = region
        self.edges.setdefault(region.name, set())

    def connect(self, a: str, b: str) -> None:
        """
        Bidirectional physical coupling.
        """
        if a not in self.regions or b not in self.regions:
            raise ValueError("Both regions must exist before connecting")

        self.edges.setdefault(a, set()).add(b)
        self.edges.setdefault(b, set()).add(a)

    # =========================================================
    # QUERIES
    # =========================================================

    def get(self, name: str) -> CoupledRegion:
        return self.regions[name]

    def neighbors(self, name: str) -> Iterable[CoupledRegion]:
        for n in self.edges.get(name, set()):
            yield self.regions[n]

    def all_regions(self) -> Iterable[CoupledRegion]:
        return self.regions.values()

    # =========================================================
    # SCUTTLING SUPPORT
    # =========================================================

    def unresolved_regions(self) -> Iterable[CoupledRegion]:
        """
        Regions that cannot currently resolve locally.
        """
        for region in self.regions.values():
            if not region.can_resolve_locally():
                yield region

    def recover_all(self, rate: float = 0.02) -> None:
        """
        Passive recovery applied globally (prebirth + idle).
        """
        for region in self.regions.values():
            region.recover(rate)

    # =========================================================
    # SNAPSHOT (FOR EMBODIMENT CANDIDATES)
    # =========================================================

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        """
        Structural snapshot of all embodied regions.

        This is the ONLY legal output used by:
        - embodiment.local.candidates.CandidateBuilder

        Format:
        {
            region_name: {
                "load": float,
                "stability": float,
                "fatigue": float,
                "integrity": float,
            }
        }
        """
        return {
            name: {
                "load": r.state.load,
                "stability": r.state.stability,
                "fatigue": r.state.fatigue,
                "integrity": r.state.integrity,
            }
            for name, r in self.regions.items()
        }