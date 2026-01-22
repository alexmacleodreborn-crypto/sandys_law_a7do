from __future__ import annotations

from typing import Set

from .graph import CouplingGraph
from .region import CoupledRegion


class CouplingPropagator:
    """
    Handles local-to-regional propagation of load, pain, or unresolved signals.

    This is a reflex-layer mechanism:
    - propagation is automatic
    - propagation is bounded
    - propagation stops once resolution occurs

    No cognition, memory, or intent is involved.
    """

    def __init__(self, graph: CouplingGraph):
        self.graph = graph

    # -------------------------------------------------
    # Core propagation
    # -------------------------------------------------

    def propagate_from(self, source: CoupledRegion) -> None:
        """
        Propagate unresolved load outward until resolved or exhausted.

        Rules:
        - propagate only if region cannot resolve locally
        - propagate to immediate neighbors
        - never revisit regions in same cycle
        """

        if source.can_resolve_locally():
            return

        visited: Set[str] = set()
        self._propagate_recursive(source, visited)

    def _propagate_recursive(
        self,
        region: CoupledRegion,
        visited: Set[str],
    ) -> None:
        if region.name in visited:
            return

        visited.add(region.name)

        # Attempt local resolution again before escalation
        if region.attempt_resolution():
            return

        # Propagate unresolved signal to neighbors
        for neighbor in self.graph.neighbors(region.name):
            neighbor.receive_propagated_signal(
                load=region.unresolved_load,
                pain=region.pain_signal,
            )

            if not neighbor.can_resolve_locally():
                self._propagate_recursive(neighbor, visited)

    # -------------------------------------------------
    # Sweep utilities
    # -------------------------------------------------

    def propagate_all(self) -> None:
        """
        Run propagation for all unresolved regions.

        This allows full-body reflex resolution without ordering assumptions.
        """
        for region in self.graph.unresolved_regions():
            self.propagate_from(region)