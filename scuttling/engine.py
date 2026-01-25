from sandys_law_a7do.scuttling.coupling.graph import CouplingGraph
from sandys_law_a7do.scuttling.local.candidates import LocalEmbodimentCandidates


class ScuttlingEngine:
    """
    Prebirth scuttling + local embodiment formation.

    NO agency
    NO choice
    NO ownership
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self.candidates = LocalEmbodimentCandidates()
        self._initialized = False

    def _init_body(self) -> None:
        from scuttling.coupling.region import CoupledRegion

        for name in ["core", "left_limb", "right_limb", "head"]:
            self.graph.add_region(CoupledRegion(name=name))

        self.graph.connect("core", "left_limb")
        self.graph.connect("core", "right_limb")
        self.graph.connect("core", "head")

        self._initialized = True

    def step(self) -> None:
        if not self._initialized:
            self._init_body()

        # passive growth
        for r in self.graph.regions.values():
            r.local_state.apply_load(0.02)
            r.local_state.recover(0.01)

        # candidate detection
        snapshot = {
            name: {
                "load": r.local_state.load,
                "pain": 1.0 - r.local_state.integrity,
                "stability": r.local_state.stability,
            }
            for name, r in self.graph.regions.items()
        }

        self.candidates.ingest_coupling_snapshot(
            snapshot=snapshot,
            support=1,
        )

    def candidates_snapshot(self) -> list:
        return self.candidates.snapshot()