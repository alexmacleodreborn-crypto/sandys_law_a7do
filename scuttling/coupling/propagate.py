# sandys_law_a7do/scuttling/coupling/propagate.py

from typing import Dict
from .region import BodyRegion
from .graph import CouplingGraph


def propagate_once(
    *,
    regions: Dict[str, BodyRegion],
    graph: CouplingGraph,
) -> None:
    """
    Single propagation step.

    - Load flows upward (decaying)
    - Stability diffuses (damped)
    """

    load_updates: Dict[str, float] = {}
    stability_updates: Dict[str, float] = {}

    for (src, dst), edge in graph.edges.items():
        a = regions.get(src)
        b = regions.get(dst)
        if not a or not b:
            continue

        load_updates[dst] = load_updates.get(dst, 0.0) + (
            a.load * edge.strength
        )

        stability_updates[dst] = stability_updates.get(dst, 0.0) + (
            a.stability * edge.damping
        )

    for name, delta in load_updates.items():
        regions[name].load = min(1.0, regions[name].load + delta)

    for name, delta in stability_updates.items():
        regions[name].stability = min(1.0, regions[name].stability + delta)