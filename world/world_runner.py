from typing import List, Optional, Tuple
from world.world_state import WorldState, WorldEventType


class WorldRunner:
    """
    Phase 0 world evolution.
    - Deterministic
    - No internal time
    - One step per external tick
    """

    def __init__(self, world: WorldState):
        self.world = world

    def step(self, action: Optional[Tuple[int, int]] = None) -> List:
        """
        Advance the world by exactly one causal step.

        action: (dx, dy) or None
        """
        events = []

        agent = self.world.agent
        cfg = self.world.cfg

        # Reset contact state
        agent.contact = False
        agent.contact_normals.clear()
        agent.thermal = 0.0
        agent.pain = 0.0

        if action is None:
            return events

        dx, dy = action
        nx, ny = agent.x + dx, agent.y + dy

        # Check bounds
        if not self.world.in_bounds(nx, ny):
            agent.effort -= cfg.block_cost
            agent.contact = True
            agent.contact_normals.append((dx, dy))

            events.append(
                self.world.emit(
                    WorldEventType.OUTCOME,
                    "blocked_by_bounds",
                    {"dx": dx, "dy": dy},
                )
            )
            return events

        # Check wall
        if self.world.has_wall_between((agent.x, agent.y), (nx, ny)):
            agent.effort -= cfg.block_cost
            agent.contact = True
            agent.contact_normals.append((dx, dy))

            events.append(
                self.world.emit(
                    WorldEventType.OUTCOME,
                    "blocked_by_wall",
                    {"dx": dx, "dy": dy},
                )
            )
            return events

        # Successful move
        agent.x = nx
        agent.y = ny
        agent.effort -= cfg.move_cost

        # Thermal contact
        surface_temp = self.world.temp_at(nx, ny)
        agent.thermal = surface_temp * cfg.contact_temp_gain

        if agent.thermal > cfg.pain_threshold:
            agent.pain = agent.thermal

        events.append(
            self.world.emit(
                WorldEventType.OUTCOME,
                "move",
                {
                    "to": (nx, ny),
                    "thermal": agent.thermal,
                    "pain": agent.pain,
                },
            )
        )

        return events
