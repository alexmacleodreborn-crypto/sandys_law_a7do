from typing import List, Optional, Tuple
from world.world_state import WorldState, WorldEventType


class WorldRunner:
    def __init__(self, world: WorldState):
        self.world = world

    def step(self, action: Optional[Tuple[int, int]] = None) -> List:
        events = []
        agent = self.world.agent
        cfg = self.world.cfg

        agent.contact = False
        agent.contact_normals.clear()
        agent.thermal = 0.0
        agent.pain = 0.0

        if action is None:
            return events

        dx, dy = action
        nx, ny = agent.x + dx, agent.y + dy

        if not self.world.in_bounds(nx, ny):
            agent.effort -= cfg.block_cost
            agent.contact = True
            agent.contact_normals.append((dx, dy))
            return events

        agent.x = nx
        agent.y = ny
        agent.effort -= cfg.move_cost

        temp = self.world.temp_at(nx, ny)
        agent.thermal = temp * cfg.contact_temp_gain

        if agent.thermal > cfg.pain_threshold:
            agent.pain = agent.thermal

        return events