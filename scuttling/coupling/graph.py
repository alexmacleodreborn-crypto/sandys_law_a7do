from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set, Iterable

from .region import CoupledRegion


@dataclass
class CouplingGraph:
    """
    Local coupling topology.

    This graph defines how embodied regions are physically and
    reflexively connected.

    The graph:
    - propagates load and signals
    - allows local resolution before escalation
    - has no concept of intention, planning, or memory

    It is a structural map, not a control system.
    """

    regions: Dict[str, CoupledRegion] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)

    # -------------------------------------------------
    # Region management
    # -------------------------------------------------

    def add_region(self, region: CoupledRegion) -> None:
        self.regions[region.name] = region
        self.edges.setdefault(region.name, set())

    def connect(self, a: str, b: str) -> None:
        """
        Create a bidirectional coupling between regions.
        """
        if a not in self.regions or b not in self.regions:
            raise ValueError("Both regions must exist before connecting")

        self.edges.setdefault(a, set()).add(b)
        self.edges.setdefault(b, set()).add(a)

    # -------------------------------------------------
    # Queries
    # -------------------------------------------------

    def neighbors(self, region: str) -> Iterable[CoupledRegion]:
        """
        Yield neighboring regions.
        """
        for name in self.edges.get(region, set()):
            yield self.regions[name]

    def get(self, name: str) -> CoupledRegion:
        return self.regions[name]

    # -------------------------------------------------
    # Local propagation support
    # -------------------------------------------------

    def unresolved_regions(self) -> Iterable[CoupledRegion]:
        """
        Regions that cannot resolve locally and may require propagation.
        """
        for region in self.regions.values():
            if not region.can_resolve_locally():
                yield region

    def clear_all_signals(self) -> None:
        """
        Clear transient signals across all regions.
        """
        for region in self.regions.values():
            region.clear_signals()