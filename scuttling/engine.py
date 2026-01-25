from __future__ import annotations

from embodiment.local.candidates import CandidateBuilder
from sandys_law_a7do.scuttling.coupling.graph import CouplingGraph
from sandys_law_a7do.scuttling.coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Prebirth embodied growth.
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()
        self._support = 0
        self._candidates = []

        self._seed()

    def _seed(self) -> None:
        core = CoupledRegion("core")
        limb_l = CoupledRegion("limb_left")
        limb_r = CoupledRegion("limb_right")

        self.graph.add_region(core)
        self.graph.add_region(limb_l)
        self.graph.add_region(limb_r)

        self.graph.connect("core", "limb_left")
        self.graph.connect("core", "limb_right")

    def step(self) -> None:
        self._support += 1

        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        self._candidates = self.builder.build_from_coupling(
            snapshot=self.graph.snapshot(),
            support=self._support,
        )

    def candidates_snapshot(self) -> list[dict]:
        return [
            {
                "kind": c.kind,
                "regions": list(c.regions),
                "support": c.support,
                "stability": round(c.stability, 3),
                "confidence": round(c.confidence_hint, 3),
            }
            for c in self._candidates
        ]