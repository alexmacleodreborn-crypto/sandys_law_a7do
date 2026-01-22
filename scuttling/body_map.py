# sandys_law_a7do/scuttling/body_map.py

from dataclasses import dataclass, field
from typing import Dict, Set


@dataclass
class BodyMap:
    """
    Pre-aware proprioceptive body structure.

    This map forms through correlated motor impulses.
    It does NOT decide movement.
    It only stabilizes structural relationships.
    """

    # Known body regions
    regions: Set[str] = field(default_factory=set)

    # Adjacency / co-activation graph
    couplings: Dict[str, Set[str]] = field(default_factory=dict)

    # Confidence that a region is "real"
    region_confidence: Dict[str, float] = field(default_factory=dict)

    # Strength of coupling between regions
    coupling_strength: Dict[str, Dict[str, float]] = field(default_factory=dict)


    # --------------------------------------------------
    # REGION FORMATION
    # --------------------------------------------------

    def add_region(self, region: str) -> None:
        if region not in self.regions:
            self.regions.add(region)
            self.region_confidence[region] = 0.1
            self.couplings.setdefault(region, set())
            self.coupling_strength.setdefault(region, {})


    # --------------------------------------------------
    # CO-ACTIVATION LEARNING
    # --------------------------------------------------

    def observe_activation(
        self,
        active_regions: Set[str],
        *,
        growth_rate: float,
    ) -> None:
        """
        Called during growth epochs when motor impulses fire.

        Regions that activate together strengthen their coupling.
        """
        for r in active_regions:
            self.add_region(r)
            self.region_confidence[r] += growth_rate * (1.0 - self.region_confidence[r])
            self.region_confidence[r] = min(1.0, self.region_confidence[r])

        for a in active_regions:
            for b in active_regions:
                if a == b:
                    continue
                self.couple(a, b, growth_rate)


    def couple(self, a: str, b: str, growth_rate: float) -> None:
        """
        Strengthen bidirectional coupling.
        """
        self.couplings.setdefault(a, set()).add(b)
        self.couplings.setdefault(b, set()).add(a)

        self.coupling_strength.setdefault(a, {})
        self.coupling_strength.setdefault(b, {})

        prev = self.coupling_strength[a].get(b, 0.1)
        new = prev + growth_rate * (1.0 - prev)

        self.coupling_strength[a][b] = min(1.0, new)
        self.coupling_strength[b][a] = self.coupling_strength[a][b]


    # --------------------------------------------------
    # LOAD-BASED DECAY
    # --------------------------------------------------

    def decay(self, structural_load: float) -> None:
        """
        High load destabilizes weak body associations.
        """
        for r in list(self.region_confidence):
            self.region_confidence[r] *= (1.0 - structural_load * 0.05)

        for a, links in self.coupling_strength.items():
            for b in list(links):
                links[b] *= (1.0 - structural_load * 0.05)


    # --------------------------------------------------
    # READ-ONLY INTROSPECTION
    # --------------------------------------------------

    def neighbors(self, region: str) -> Set[str]:
        return self.couplings.get(region, set())

    def confidence(self, region: str) -> float:
        return self.region_confidence.get(region, 0.0)