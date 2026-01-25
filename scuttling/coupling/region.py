from __future__ import annotations
from dataclasses import dataclass, field

from .local_state import LocalState


@dataclass
class CoupledRegion:
    """
    Structural region node in the scuttling graph.

    - Owns a LocalState (physics)
    - Participates in coupling topology
    - Does NOT reason or decide
    """

    name: str
    state: LocalState = field(default_factory=LocalState)

    # -------------------------------------------------
    # Pass-through physiology
    # -------------------------------------------------

    def recover(self, rate: float = 0.02) -> None:
        self.state.recover(rate)

    def apply_load(self, delta: float) -> None:
        self.state.apply_load(delta)

    def relieve_load(self, delta: float) -> None:
        self.state.relieve_load(delta)

    # -------------------------------------------------
    # Structural checks
    # -------------------------------------------------

    def can_resolve_locally(self) -> bool:
        return not (self.state.overloaded() or self.state.unstable())

    def clear_signals(self) -> None:
        """
        Reserved for transient signal clearing.
        (No-op for now.)
        """
        pass