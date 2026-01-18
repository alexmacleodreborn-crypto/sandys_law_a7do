from __future__ import annotations

from typing import List, Tuple

from world.world_state import WorldEventType, WorldEvent, WorldState
from world.space import GridSpace, Vec2


# ============================================================
# Phase 0: Physics
# - Applies actions to the world
# - Emits ACTION + OUTCOME events
# - Updates body contact state
# - NO learning, NO time, NO memory
# ============================================================


class WorldPhysics:
    """
    Deterministic physics engine.
    Translates actions into outcomes and updates world state.
    """

    def __init__(self, state: WorldState) -> None:
        self.state = state
        self.space = GridSpace(state)

    # --------------------------------------------------------
    # Action application
    # --------------------------------------------------------

    def apply_move(self, dx: int, dy: int) -> List[WorldEvent]:
        """
        Attempt to move the agent by (dx, dy).
        Emits:
          - ACTION: move
          - OUTCOME: moved | blocked
        """
        events: List[WorldEvent] = []

        agent = self.state.agent
        start_pos = (agent.x, agent.y)
        delta: Vec2 = (dx, dy)

        # --- ACTION EVENT ---
        act = self.state.emit(
            type=WorldEventType.ACTION,
            name="move",
            payload={
                "dx": dx,
                "dy": dy,
                "from": start_pos,
            },
        )
        events.append(act)

        # --- PHYSICS CHECK ---
        ok, new_pos, reason = self.space.validate_move(start_pos, delta)

        if ok:
            # Successful move
            agent.x, agent.y = new_pos
            agent.effort = max(0.0, agent.effort - self.state.cfg.move_cost)

            outcome = self.state.emit(
                type=WorldEventType.OUTCOME,
                name="moved",
                payload={
                    "to": new_pos,
                    "cost": self.state.cfg.move_cost,
                },
                parent_id=act.event_id,
            )
            events.append(outcome)
        else:
            # Blocked move
            agent.effort = max(0.0, agent.effort - self.state.cfg.block_cost)

            outcome = self.state.emit(
                type=WorldEventType.OUTCOME,
                name="blocked",
                payload={
                    "reason": reason,
                    "attempted_delta": delta,
                    "cost": self.state.cfg.block_cost,
                },
                parent_id=act.event_id,
            )
            events.append(outcome)

        # ----------------------------------------------------
        # Contact update (continuous wall detection)
        # ----------------------------------------------------

        report = self.space.contact_at((agent.x, agent.y))
        agent.contact = report.contact
        agent.contact_normals = report.normals

        # ----------------------------------------------------
        # Thermal + pain placeholders (no semantics yet)
        # ----------------------------------------------------

        if agent.contact:
            # Temperature only meaningful when touching something
            local_temp = self.state.temp_at(agent.x, agent.y)
            agent.thermal = self.state.cfg.contact_temp_gain * local_temp
        else:
            agent.thermal = 0.0

        # Pain is only a physical overload signal (NOT emotion)
        if agent.effort <= 0.0:
            agent.pain = 1.0
        else:
            agent.pain = 0.0

        return events
