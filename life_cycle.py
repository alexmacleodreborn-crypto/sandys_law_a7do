"""
A7DO Full Life Cycle (Clock-Correct)
===================================

This LifeCycle DOES NOT own time.
It delegates to the canonical step_tick().
"""

from engine.tick_engine import TickEngine

from world.world_state import make_default_world
from world.world_runner import WorldRunner


class LifeCycle:
    """
    Observer + coordinator around the real clock.
    """

    def __init__(self):
        # Canonical system state
        self.engine = TickEngine()
        self.state = self.engine.snapshot()

        # World (Phase 0)
        self.world = make_default_world()
        self.world_runner = WorldRunner(self.world)

    # ----------------------------------------------
    # ONE HEARTBEAT
    # ----------------------------------------------

    def tick(self):
        # Advance canonical system clock
        self.engine.tick()

        # World physics step (no semantics)
        self.world_runner.step(action=None)

    # ----------------------------------------------
    # RUN LOOP
    # ----------------------------------------------

    def run(self, max_ticks: int | None = None):
        ticks = 0
        while True:
            self.tick()
            ticks += 1

            if max_ticks is not None and ticks >= max_ticks:
                break