"""
A7DO Full Life Cycle (Clock-Correct)
===================================

This LifeCycle DOES NOT own time.
It delegates to the canonical step_tick().
"""

from __future__ import annotations
from enum import Enum

from sandys_law_a7do.engine.tick_engine import TickEngine
from sandys_law_a7do.world.world_state import make_default_world


class LifePhase(Enum):
    WOMB = "womb"
    BORN = "born"


class LifeCycle:
    """
    High-level lifecycle coordinator.

    Responsibilities:
    - Own TickEngine
    - Expose phase & born state
    - Own world instance
    """

    def __init__(self):
        self.world = make_default_world()
        self.engine = TickEngine()
        self.phase = LifePhase.WOMB
        self.born = False

    def tick(self) -> None:
        self.engine.tick()

        birth = self.engine.state.get("birth_state")
        if birth and birth.born:
            self.born = True
            self.phase = LifePhase.BORN