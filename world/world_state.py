from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from map.world_map import WorldMap


class WorldEventType(str, Enum):
    OBSERVATION = "observation"
    ACTION = "action"
    OUTCOME = "outcome"
    SYSTEM = "system"


@dataclass(frozen=True)
class WorldEvent:
    event_id: str
    type: WorldEventType
    name: str
    payload: Dict[str, Any]
    parent_id: Optional[str] = None


@dataclass
class AgentBody:
    x: int
    y: int
    effort: float = 1.0

    contact: bool = False
    contact_normals: List[Tuple[int, int]] = field(default_factory=list)
    thermal: float = 0.0
    pain: float = 0.0


@dataclass
class WorldConfig:
    width: int = 11
    height: int = 11

    contact_temp_gain: float = 0.6
    pain_threshold: float = 0.85
    move_cost: float = 0.10
    block_cost: float = 0.20


@dataclass
class WorldState:
    cfg: WorldConfig
    agent: AgentBody
    world_map: WorldMap

    walls: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = field(default_factory=set)
    _event_counter: int = 0

    def next_event_id(self, prefix: str = "w") -> str:
        self._event_counter += 1
        return f"{prefix}{self._event_counter:08d}"

    def emit(
        self,
        type: WorldEventType,
        name: str,
        payload: Dict[str, Any],
        parent_id: Optional[str] = None,
    ) -> WorldEvent:
        return WorldEvent(
            event_id=self.next_event_id(),
            type=type,
            name=name,
            payload=payload,
            parent_id=parent_id,
        )

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cfg.width and 0 <= y < self.cfg.height

    def temp_at(self, x: int, y: int) -> float:
        env = self.world_map.environment_at(x, y)
        return env.temperature