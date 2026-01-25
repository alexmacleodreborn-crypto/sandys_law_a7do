from __future__ import annotations

from embodiment.local.candidates import CandidateBuilder
from sandys_law_a7do.scuttling.coupling.graph import CouplingGraph
from sandys_law_a7do.scuttling.coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Scuttling Engine — Prebirth Structural Growth

    Responsibilities:
    - maintain coupling graph
    - propagate load / stability
    - generate LOCAL embodiment candidates

    This engine:
    - does NOT consolidate
    - does NOT touch embodiment ledger
    - does NOT gate
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()
        self._support_counter = 0
        self._local_candidates = []

        # --------------------------------------------------
        # INITIAL BODY SEED (PREBIRTH)
        # --------------------------------------------------
        self._seed_body()

    # --------------------------------------------------
    # Body seed (minimal fetus-like structure)
    # --------------------------------------------------

    def _seed_body(self) -> None:
        core = CoupledRegion(name="core")
        limb = CoupledRegion(name="limb")

        self.graph.add_region(core)
        self.graph.add_region(limb)
        self.graph.connect("core", "limb")

    # --------------------------------------------------
    # Step (called every tick before birth)
    # --------------------------------------------------

    def step(self) -> None:
        """
        Advance local embodied growth.
        """
        self._support_counter += 1

        # Passive stabilization
        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        # Build local candidates
        snapshot = self.graph.snapshot()

        self._local_candidates = self.builder.build_from_coupling(
            snapshot=snapshot,
            support=self._support_counter,
        )

    # --------------------------------------------------
    # Read-only exposure
    # --------------------------------------------------

    def candidates_snapshot(self):
        """
        Safe, read-only view for dashboard / bootstrap.
        """
        return [
            {
                "kind": c.kind,
                "regions": list(c.regions),
                "conditions": list(c.conditions),
                "support": c.support,
                "stability": round(c.stability, 3),
                "confidence_hint": round(c.confidence_hint, 3),
            }
            for c in self._local_candidates
        ]