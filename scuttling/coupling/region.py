"""
CoupledRegion
=============

Local embodied region used by scuttling and reflex coupling.

This file intentionally exposes BOTH:
- flat attributes (load, pain, thermal)
- a `.state` view for graph compatibility
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, Optional, Set


# --------------------------------------------------
# Internal state view (graph expects this)
# --------------------------------------------------

@dataclass
class RegionState:
    load: float = 0.0
    pain: float = 0.0
    thermal: float = 0.0
    contact: bool = False


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
    thermal: float = 0.0
    contact: bool = False

    # -------------------------
    # Coupling
    # -------------------------
    neighbours: Set[str] = field(default_factory=set)
    coupling_strength: Dict[str, float] = field(default_factory=dict)

    # -------------------------
    # Internal
    # -------------------------
    active: bool = True
    state: RegionState = field(default_factory=RegionState)

    # --------------------------------------------------
    # Synchronisation
    # --------------------------------------------------

    def _sync_state(self) -> None:
        """
        Keep state view consistent with flat attributes.
        """
        self.state.load = self.load
        self.state.pain = self.pain
        self.state.thermal = self.thermal
        self.state.contact = self.contact

    # --------------------------------------------------
    # Signal update
    # --------------------------------------------------

    def update_signals(
        self,
        *,
        load: Optional[float] = None,
        pain: Optional[float] = None,
        thermal: Optional[float] = None,
        contact: Optional[bool] = None,
    ) -> None:
        if load is not None:
            self.load = max(0.0, float(load))
        if pain is not None:
            self.pain = max(0.0, float(pain))
        if thermal is not None:
            self.thermal = max(0.0, float(thermal))
        if contact is not None:
            self.contact = bool(contact)

        self._sync_state()

    # --------------------------------------------------
    # Recovery / decay
    # --------------------------------------------------

    def recover(self, rate: float = 0.01) -> None:
        r = max(0.0, float(rate))

        self.load = max(0.0, self.load - r)
        self.pain = max(0.0, self.pain - r)
        self.thermal = max(0.0, self.thermal - r)

        self.contact = False
        self._sync_state()

    # --------------------------------------------------
    # Coupling management
    # --------------------------------------------------

    def couple_to(self, other: "CoupledRegion", strength: float = 1.0) -> None:
        s = max(0.0, float(strength))

        self.neighbours.add(other.name)
        other.neighbours.add(self.name)

        self.coupling_strength[other.name] = s
        other.coupling_strength[self.name] = s

    # --------------------------------------------------
    # Propagated load
    # --------------------------------------------------

    def propagated_load(self) -> float:
        base = self.load + self.pain
        if self.contact:
            base += self.thermal
        return max(0.0, base)

    # --------------------------------------------------
    # Snapshot (UI safe)
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