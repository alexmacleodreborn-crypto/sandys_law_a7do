# sandys_law_a7do/embodiment/local/regions.py
"""
Local Body Regions — Phase A4 (LOCKED)

Defines:
- What constitutes a local body region
- Ownership eligibility
- Hierarchical coupling (finger → hand → shoulder → spine)
- Signal propagation direction (local → regional → spine)

This file contains NO control logic.
This file contains NO learning.
This file contains NO gates.

It is structural ground truth.
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Set, Iterable


# ============================================================
# REGION DEFINITIONS
# ============================================================

@dataclass(frozen=True)
class BodyRegion:
    """
    A structural body region.

    This does NOT imply ownership.
    This does NOT imply control.
    """
    name: str


@dataclass(frozen=True)
class LocalRegion(BodyRegion):
    """
    A locally owned body region.

    Properties:
    - Direct sensory feedback
    - Local control eligibility
    - Embodiment candidate
    """
    locally_controllable: bool = True
    sensory_capable: bool = True


# ============================================================
# REGION GRAPH (STRUCTURE ONLY)
# ============================================================

@dataclass
class RegionGraph:
    """
    Directed coupling graph of body regions.

    Rules:
    - Child → Parent propagation only
    - No cycles
    - No semantic meaning
    """

    parents: Dict[str, str] = field(default_factory=dict)
    children: Dict[str, Set[str]] = field(default_factory=dict)

    # ----------------------------
    # Registration
    # ----------------------------

    def add_region(self, region: BodyRegion) -> None:
        self.children.setdefault(region.name, set())

    def couple(self, child: str, parent: str) -> None:
        self.parents[child] = parent
        self.children.setdefault(parent, set()).add(child)
        self.children.setdefault(child, set())

    # ----------------------------
    # Queries
    # ----------------------------

    def parent_of(self, region: str) -> str | None:
        return self.parents.get(region)

    def children_of(self, region: str) -> Set[str]:
        return self.children.get(region, set())

    def lineage(self, region: str) -> Iterable[str]:
        """
        Walk upward toward spine.
        """
        current = region
        while current in self.parents:
            parent = self.parents[current]
            yield parent
            current = parent


# ============================================================
# DEFAULT HUMAN-LIKE LOCAL MAP (v1)
# ============================================================

def default_local_body_map() -> RegionGraph:
    """
    Defines the minimal local → regional → spine structure.

    Local:
    - fingers
    - hand
    - shoulder

    Non-local:
    - forearm (muscle conduit, no ownership)

    Central:
    - spine
    """

    g = RegionGraph()

    # Core
    g.add_region(BodyRegion("spine"))

    # Upper limb
    g.add_region(LocalRegion("shoulder"))
    g.add_region(BodyRegion("forearm"))   # intentionally NOT local
    g.add_region(LocalRegion("hand"))

    # Fingers
    for i in range(1, 6):
        g.add_region(LocalRegion(f"finger_{i}"))

    # Couplings
    g.couple("finger_1", "hand")
    g.couple("finger_2", "hand")
    g.couple("finger_3", "hand")
    g.couple("finger_4", "hand")
    g.couple("finger_5", "hand")

    g.couple("hand", "forearm")
    g.couple("forearm", "shoulder")
    g.couple("shoulder", "spine")

    return g