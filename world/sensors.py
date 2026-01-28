from typing import List
from world.world_state import WorldEventType, WorldState, WorldEvent


class SensorSuite:
    def __init__(self, state: WorldState):
        self.state = state

    def sense(self) -> List[WorldEvent]:
        events: List[WorldEvent] = []
        agent = self.state.agent

        if agent.contact:
            events.append(
                self.state.emit(
                    WorldEventType.OBSERVATION,
                    "contact",
                    {"count": float(len(agent.contact_normals))},
                )
            )

        env = self.state.world_map.environment_at(agent.x, agent.y)

        if env.noise > 0.0:
            events.append(
                self.state.emit(
                    WorldEventType.OBSERVATION,
                    "noise",
                    {"level": env.noise},
                )
            )

        return events