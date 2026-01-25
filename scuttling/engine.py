from __future__ import annotations

from scuttling.coupling.graph import CouplingGraph
from scuttling.coupling.region import CoupledRegion


class ScuttlingEngine:
    """
    Prebirth scuttling engine.

    Responsibilities:
    - Maintain coupling graph
    - Apply passive growth + load
    - Produce structural snapshot

    NO cognition
    NO learning
    NO decisions
    """

    def __init__(self) -> None:
        self.graph = CouplingGraph()
        self._initialized = False

    def _init_body(self) -> None:
        """
        Minimal embryonic topology.
        """
        for name in [
            "core",
            "left_limb",
            "right_limb",
            "head",
        ]:
            self.graph.add_region(CoupledRegion(name=name))

        self.graph.connect("core", "left_limb")
        self.graph.connect("core", "right_limb")
        self.graph.connect("core", "head")

        self._initialized = True

    def step(self) -> None: