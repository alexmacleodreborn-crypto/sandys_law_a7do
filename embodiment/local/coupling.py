from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Set, Iterable


# ============================================================
# Coupling Doctrine
#
# Coupling is:
# - local
# - structural
# - non-symbolic
# - non-decisional
#
# Coupling does NOT:
# - trigger gates
# - write memory
# - reason
# - plan
#
# Coupling EXISTS to:
# - propagate load, pain, and instability
# - aggregate local signals upward
# - distribute stabilization downward
#
# Think: nervous system routing, not cognition.
# ============================================================


# ------------------------------------------------------------
# Coupling Signal
# ------------------------------------------------------------

@dataclass(frozen=True)
class CouplingSignal:
    """
    Structural signal propagated between regions.
    """
    kind: str              # "load", "pain", "stability"
    magnitude: float       # normalized [0..1]
    source_region: str


# ------------------------------------------------------------
# Coupled Region
# ------------------------------------------------------------

@dataclass
class CoupledRegion:
    """
    A body region participating in local coupling.
    """
    name: str
    parent: str | None = None
    children: Set[str] = field(default_factory=set)

    # Aggregated local state
    load: float = 0.0
    pain: float = 0.0
    stability: float = 1.0


# ------------------------------------------------------------
# Coupling Graph
# ------------------------------------------------------------

class CouplingGraph:
    """
    Defines hierarchical coupling between body regions.

    Example:
        finger -> hand -> wrist -> shoulder
    """

    def __init__(self) -> None:
        self._regions: Dict[str, CoupledRegion] = {}

    # --------------------------------------------------------
    # Region registration
    # --------------------------------------------------------

    def add_region(
        self,
        *,
        name: str,
        parent: str | None = None,
    ) -> None:
        if name not in self._regions:
            self._regions[name] = CoupledRegion(name=name)

        if parent is not None:
            if parent not in self._regions:
                self._regions[parent] = CoupledRegion(name=parent)

            self._regions[name].parent = parent
            self._regions[parent].children.add(name)

    # --------------------------------------------------------
    # Signal propagation (UPWARD)
    # --------------------------------------------------------

    def propagate_up(self, signal: CouplingSignal) -> None:
        """
        Propagate a local signal upward through the coupling graph.

        This is how:
        - finger pain reaches hand
        - hand overload reaches wrist
        - shoulder instability reaches spine (later)
        """

        region_name = signal.source_region

        while region_name is not None:
            region = self._regions.get(region_name)
            if region is None:
                break

            self._apply_signal(region, signal)
            region_name = region.parent

    # --------------------------------------------------------
    # Stabilization propagation (DOWNWARD)
    # --------------------------------------------------------

    def propagate_down(
        self,
        *,
        region_name: str,
        stability_delta: float,
    ) -> None:
        """
        Distribute stabilization downward.

        Example:
        - wrist stabilizes hand
        - hand stabilizes fingers
        """

        region = self._regions.get(region_name)
        if region is None:
            return

        for child in region.children:
            child_region = self._regions[child]
            child_region.stability = min(
                1.0,
                child_region.stability + stability_delta,
            )
            self.propagate_down(
                region_name=child,
                stability_delta=stability_delta * 0.5,  # dampening
            )

    # --------------------------------------------------------
    # Internal application logic
    # --------------------------------------------------------

    @staticmethod
    def _apply_signal(region: CoupledRegion, signal: CouplingSignal) -> None:
        if signal.kind == "load":
            region.load = min(1.0, region.load + signal.magnitude * 0.6)

        elif signal.kind == "pain":
            region.pain = min(1.0, region.pain + signal.magnitude)
            region.stability = max(0.0, region.stability - signal.magnitude * 0.3)

        elif signal.kind == "stability":
            region.stability = min(1.0, region.stability + signal.magnitude)

    # --------------------------------------------------------
    # Snapshot (for candidates / consolidation)
    # --------------------------------------------------------

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        """
        Return a structural snapshot of all regions.

        Used by:
        - candidates.py
        - consolidation gate (later)
        """

        return {
            name: {
                "load": r.load,
                "pain": r.pain,
                "stability": r.stability,
            }
            for name, r in self._regions.items()
        }