from __future__ import annotations
from enum import Enum

from engine.tick_engine import TickEngine
from world.world_state import make_default_world


class LifePhase(Enum):
    """
    High-level lifecycle phase.
    """
    WOMB = "womb"
    BORN = "born"


class LifeCycle:
    """
    Authoritative lifecycle coordinator.

    Responsibilities:
    - Own the TickEngine
    - Own the physical world instance
    - Track phase (womb → born)
    - Expose minimal public state for observers
    """

    def __init__(self) -> None:
        # Physical world (external, persistent)
        self.world = make_default_world()

        # Temporal engine (authoritative)
        self.engine = TickEngine()

        # Lifecycle flags
        self.phase: LifePhase = LifePhase.WOMB
        self.born: bool = False

    def tick(self) -> None:
        """
        Advance the system by exactly one tick.
        """
        self.engine.tick()

        # Update lifecycle flags deterministically
        birth_state = self.engine.state.get("birth_state")
        if birth_state and birth_state.born:
            self.born = True
            self.phase = LifePhase.BORN