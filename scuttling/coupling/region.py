"""
CoupledRegion
=============

Local embodied region used by scuttling and reflex coupling.

Phase constraints:
- No cognition
- No planning
- No semantics
- Pure local state + signal decay / propagation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Set


@dataclass
class CoupledRegion:
    """
    A minimal local coupling region.
    """

    name: str

    # -------------------------
    # Local embodied signals
    # -------------------------
    load: float = 0.0
    pain: float = 0.0
    contact: bool = False
    thermal: float = 0.0

    # -------------------------
    # Coupling
    # -------------------------
    neighbours: Set[str] = field(default_factory=set)
    coupling_strength: Dict[str, float] = field(default_factory=dict)

    # -------------------------
    # Internal state
    # -------------------------
    active: bool = True

    # --------------------------------------------------
    # Signal update
    # --------------------------------------------------

    def update_signals(
        self,
        *,
        load: Optional[float] = None,
        pain: Optional[float] = None,
        contact: Optional[bool] = None,
        thermal: Optional[float] = None,
    ) -> None:
        if load is not None:
            self.load = max(0.0, float(load))
        if pain is not None:
            self.pain = max(0.0, float(pain))
        if contact is not None:
            self.contact = bool(contact)
        if thermal is not None:
            self.thermal = max(0.0, float(thermal))

    # --------------------------------------------------
    # Recovery / decay (THIS FIXES THE ERROR)
    # --------------------------------------------------

    def recover(self, rate: float = 0.01) -> None:
        """
        Passive recovery toward baseline.

        This represents:
        - tissue relaxation
        - neural settling
        - load dissipation

        No learning, no decisions.
        """

        r = max(0.0, float(rate))

        self.load = max(0.0, self.load - r)
        self.pain = max(0.0, self.pain - r)
        self.thermal = max(0.0, self.thermal - r)

        # Contact resets unless refreshed externally
        self.contact = False

    # --------------------------------------------------
    # Coupling management
    # --------------------------------------------------

    def couple_to(self, other: "CoupledRegion", strength: float = 1.0) -> None:
        self.neighbours.add(other.name)
        other.neighbours.add(self.name)

        s = max(0.0, float(strength))
        self.coupling_strength[other.name] = s
        other.coupling_strength[self.name] = s

    # --------------------------------------------------
    # Propagated load (conservative)
    # --------------------------------------------------

    def propagated_load(self) -> float:
        base = self.load + self.pain
        if self.contact:
            base += self.thermal
        return max(0.0, base)

    # --------------------------------------------------
    # Snapshot (UI / debug safe)
    # --------------------------------------------------

    def snapshot(self) -> Dict[str, object]:
        return {
            "name": self.name,
            "active": self.active,
            "load": self.load,
            "pain": self.pain,
            "thermal": self.thermal,
            "contact": self.contact,
            "neighbours": list(self.neighbours),
            "coupling_strength": dict(self.coupling_strength),
        }