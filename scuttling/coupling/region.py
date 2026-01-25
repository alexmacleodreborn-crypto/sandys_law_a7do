from __future__ import annotations

from dataclasses import dataclass, field
from .local_state import LocalState


@dataclass
class CoupledRegion:
    """
    A named embodied region that participates in coupling.

    This is NOT cognition.
    This is NOT memory.
    This is a physical / reflexive unit.
    """

    name: str
    state: LocalState = field(default_factory=LocalState)

    # -------------------------------------------------
    # Signal handling
    # -------------------------------------------------

    def can_resolve_locally(self) -> bool:
        """
        Whether this region can handle its current state
        without propagating upward.
        """
        return not (
            self.state.overloaded()
            or self.state.unstable()
            or self.state.exhausted()
        )

    def clear_signals(self) -> None:
        """
        Clear transient stress via passive recovery.
        """
        self.state.recover()