from __future__ import annotations

from embodiment.local.candidates import CandidateBuilder
from sandys_law_a7do.scuttling.coupling.graph import CouplingGraph
from sandys_law_a7do.scuttling.coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Scuttling Engine — Prebirth Embodied Growth

    Responsibilities:
    - maintain local coupling graph
    - propagate recovery and load
    - generate LOCAL embodiment candidates

    This engine:
    - does NOT perceive
    - does NOT reason
    - does NOT consolidate
    - does NOT know about frames, memory, or preference
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()

        self._support_counter = 0
        self._local_candidates = []

        self._seed_body()

    # --------------------------------------------------
    # Initial fetal body seed
    # --------------------------------------------------

    def _seed_body(self) -> None:
        """
        Minimal prebirth structure.
        This will expand later.
        """
        core = CoupledRegion(name="core")
        limb = CoupledRegion(name="limb")

        self.graph.add_region(core)
        self.graph.add_region(limb)
        self.graph.connect("core", "limb")

    # --------------------------------------------------
    # Step (called by bootstrap.tick_system)
    # --------------------------------------------------

    def step(self) -> None:
        """
        Advance embodied physics by one tick.
        """
        self._support_counter += 1

        # Passive recovery across regions
        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        # Snapshot local physics
        snapshot = self.graph.snapshot()

        # Build LOCAL candidates (no consolidation)
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