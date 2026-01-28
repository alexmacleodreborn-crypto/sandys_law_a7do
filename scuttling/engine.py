from embodiment.local.candidates import CandidateBuilder
from .coupling.graph import CouplingGraph
from .coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Pre-birth embodied structural growth.

    Scuttling:
    - does NOT decide
    - does NOT act
    - does NOT perceive meaning
    - ONLY stabilizes body-like structure
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.builder = CandidateBuilder()
        self._support = 0
        self._candidates = []
        self._seed_regions()

    # --------------------------------------------------
    # INITIAL BODY SEED
    # --------------------------------------------------

    def _seed_regions(self) -> None:
        """
        Create minimal proto-body regions.
        """
        core = CoupledRegion(name="core")
        limb = CoupledRegion(name="limb")

        self.graph.add_region(core)
        self.graph.add_region(limb)
        self.graph.connect("core", "limb")

    # --------------------------------------------------
    # STEP (CALLED EVERY TICK)
    # --------------------------------------------------

    def step(self) -> None:
        """
        Advance embodied structural stability.
        """
        self._support += 1

        # Structural recovery
        for region in self.graph.regions.values():
            region.recover(rate=0.01)

        # Snapshot coupling graph
        snapshot = self.graph.snapshot()

        # Build candidates from structure
        self._candidates = self.builder.build_from_coupling(
            snapshot=snapshot,
            support=self._support,
        )

    # --------------------------------------------------
    # UI / OBSERVER SAFE SNAPSHOT
    # --------------------------------------------------

    def candidates_snapshot(self):
        """
        Read-only snapshot for dashboards and observers.
        """
        if not self._candidates:
            return []

        return [
            {
                "kind": c.kind,
                "regions": list(c.regions),
                "support": c.support,
                "stability": round(c.stability, 3),
            }
            for c in self._candidates
        ]