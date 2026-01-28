from embodiment.local.candidates import CandidateBuilder
from .coupling.graph import CouplingGraph
from .coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Pre-cognitive body schema formation.

    This runs continuously.
    It does NOT decide actions.
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()
        self._support = 0
        self._candidates = []
        self._seed()

    def _seed(self):
        core = CoupledRegion(name="core")
        limb = CoupledRegion(name="limb")
        self.graph.add_region(core)
        self.graph.add_region(limb)
        self.graph.connect("core", "limb")

    def step(self) -> None:
        self._support += 1

        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        snapshot = self.graph.snapshot()
        self._candidates = self.builder.build_from_coupling(
            snapshot=snapshot,
            support=self._support,
        )

    def candidates_snapshot(self):
        return [
            {
                "kind": c.kind,
                "regions": list(c.regions),
                "support": c.support,
                "stability": round(c.stability, 3),
            }
            for c in self._candidates
        ]