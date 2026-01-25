from __future__ import annotations

from embodiment.local.candidates import CandidateBuilder
from sandys_law_a7do.scuttling.coupling.graph import CouplingGraph
from sandys_law_a7do.scuttling.coupling.region import CoupledRegion
from genesis.prebirth.phases import phase_for_tick, PrebirthPhase


class ScuttlingEngine:
    """
    Prebirth embodied growth engine.
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()
        self._support = 0
        self._candidates = []
        self._last_phase = None

    def _seed_phase(self, phase: PrebirthPhase) -> None:
        if phase == PrebirthPhase.NEURAL_PLATE:
            self.graph.add_region(CoupledRegion("neural_core"))

        elif phase == PrebirthPhase.CORE:
            self.graph.add_region(CoupledRegion("core"))
            self.graph.connect("neural_core", "core")

        elif phase == PrebirthPhase.LIMB_BUDS:
            self.graph.add_region(CoupledRegion("limb_left"))
            self.graph.add_region(CoupledRegion("limb_right"))
            self.graph.connect("core", "limb_left")
            self.graph.connect("core", "limb_right")

        elif phase == PrebirthPhase.LIMB_EXTENSION:
            self.graph.add_region(CoupledRegion("hand_left"))
            self.graph.add_region(CoupledRegion("hand_right"))
            self.graph.connect("limb_left", "hand_left")
            self.graph.auto = True
            self.graph.connect("limb_right", "hand_right")

    def step(self, *, tick: int) -> None:
        self._support += 1
        phase = phase_for_tick(tick)

        if phase != self._last_phase:
            self._seed_phase(phase)
            self._last_phase = phase

        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        self._candidates = self.builder.build_from_coupling(
            snapshot=self.graph.snapshot(),
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