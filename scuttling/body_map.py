# sandys_law_a7do/scuttling/body_map.py

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class BodyMap:
    """
    Structural representation of controllable body regions.
    """
    regions: Set[str] = field(default_factory=set)
    couplings: Dict[str, Set[str]] = field(default_factory=dict)

    def add_region(self, region: str) -> None:
        self.regions.add(region)

    def couple(self, a: str, b: str) -> None:
        self.couplings.setdefault(a, set()).add(b)
        self.couplings.setdefault(b, set()).add(a)

    def neighbors(self, region: str) -> Set[str]:
        return self.couplings.get(region, set())
