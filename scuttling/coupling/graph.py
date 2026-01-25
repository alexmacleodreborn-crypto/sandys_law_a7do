from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set
from .region import CoupledRegion


@dataclass
class CouplingGraph:
    regions: Dict[str, CoupledRegion] = field(default_factory=dict)
    edges: Dict[str, Set[str]] = field(default_factory=dict)

    def add_region(self, region: CoupledRegion) -> None:
        self.regions[region.name] = region
        self.edges.setdefault(region.name, set())

    def connect(self, a: str, b: str) -> None:
        self.edges.setdefault(a, set()).add(b)
        self.edges.setdefault(b, set()).add(a)

    def snapshot(self) -> dict:
        return {
            name: {
                "load": r.state.load,
                "pain": 1.0 - r.state.stability,
                "stability": r.state.stability,
            }
            for name, r in self.regions.items()
        }