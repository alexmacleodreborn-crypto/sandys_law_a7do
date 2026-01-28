"""
CoupledRegion
=============

Defines a local embodied region for scuttling / reflex coupling.

Phase constraints:
- No cognition
- No planning
- No semantics
- Pure local state + signal propagation
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class CoupledRegion:
    """
    A minimal local coupling region.

    Represents:
    - a body-local zone
    - reflex-relevant signals
    - coupling strength to neighbours

    This is NOT a cognitive structure.
    """

    name: str

    # -------------------------
    # Local signals
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
    # Update local sensory signals
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
            self.load = float(load)
        if pain is not None:
            self.pain = float(pain)
        if contact is not None:
            self.contact = bool(contact)
        if thermal is not None:
            self.thermal = float(thermal)

    # --------------------------------------------------
    # Coupling management
    # --------------------------------------------------

    def couple_to(self, other: "CoupledRegion", strength: float = 1.0) -> None:
        """
        Create bidirectional coupling between regions.
        """
        self.neighbours.add(other.name)
        other.neighbours.add(self.name)

        self.coupling_strength[other.name] = float(strength)
        other.coupling_strength[self.name] = float(strength)

    # --------------------------------------------------
    # Signal propagation (purely local)
    # --------------------------------------------------

    def propagated_load(self) -> float:
        """
        Compute local propagated load signal.
        Conservative: no amplification.
        """
        base = self.load + self.pain + (self.thermal if self.contact else 0.0)
        return max(0.0, base)

    # --------------------------------------------------
    # Snapshot (debug / UI safe)
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