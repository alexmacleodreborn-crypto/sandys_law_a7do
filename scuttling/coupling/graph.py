# sandys_law_a7do/scuttling/coupling/graph.py

from dataclasses import dataclass
from typing import Dict, Tuple

@dataclass(frozen=True)
class CouplingEdge:
    """
    Defines structural coupling between two regions.
    """
    strength: float   # load propagation factor
    damping: float    # stability propagation factor


class CouplingGraph:
    """
    Directed, weighted coupling graph.
    """

    def __init__(self):
        self.edges: Dict[Tuple[str, str], CouplingEdge] = {}

    def connect(
        self,
        src: str,
        dst: str,
        *,
        strength: float,
        damping: float,
    ) -> None:
        self.edges[(src, dst)] = CouplingEdge(
            strength=strength,
            damping=damping,
        )

    def edge(self, src: str, dst: str) -> CouplingEdge | None:
        return self.edges.get((src, dst))