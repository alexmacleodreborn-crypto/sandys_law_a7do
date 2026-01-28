from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple

from world.layouts.map.world_map import WorldMap


# ============================================================
# WORLD EVENTS (Phase 0)
# ============================================================

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


# ============================================================
# AGENT BODY (Pure physics)
# ============================================================

@dataclass
class AgentBody:
    x: int
    y: int
    effort: float = 1.0

    contact: bool = False
    contact_normals: List[Tuple[int, int]] = field(default_factory=list)
    thermal: float = 0.0
    pain: float = 0.0


# ============================================================
# WORLD CONFIG
# ============================================================

@dataclass
class WorldConfig:
    width: int = 11
    height: int = 11

    contact_temp_gain: float = 0.6
    pain_threshold: float = 0.85
    move_cost: float = 0.10
    block_cost: float = 0.20


# ============================================================
# WORLD STATE (Authoritative)
# ============================================================

@dataclass
class WorldState:
    cfg: WorldConfig
    agent: AgentBody
    world_map: WorldMap

    walls: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = field(default_factory=set)
    _event_counter: int = 0

    # --------------------------------------------------------
    # Event system (deterministic)
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # Geometry helpers
    # --------------------------------------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cfg.width and 0 <= y < self.cfg.height

    @staticmethod
    def _canon_edge(
        a: Tuple[int, int], b: Tuple[int, int]
    ) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (a, b) if a <= b else (b, a)

    def has_wall_between(
        self, a: Tuple[int, int], b: Tuple[int, int]
    ) -> bool:
        return self._canon_edge(a, b) in self.walls

    def add_wall_between(
        self, a: Tuple[int, int], b: Tuple[int, int]
    ) -> None:
        self.walls.add(self._canon_edge(a, b))

    # --------------------------------------------------------
    # Environment
    # --------------------------------------------------------

    def temp_at(self, x: int, y: int) -> float:
        env = self.world_map.environment_at(x, y)
        return float(env.temperature)

    # --------------------------------------------------------
    # Snapshot (UI / debugging only)
    # --------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        return {
            "agent": {
                "x": self.agent.x,
                "y": self.agent.y,
                "effort": self.agent.effort,
                "contact": self.agent.contact,
                "thermal": self.agent.thermal,
                "pain": self.agent.pain,
            },
            "event_counter": self._event_counter,
        }


# ============================================================
# DEFAULT WORLD CONSTRUCTOR  🔴 REQUIRED
# ============================================================

def make_default_world(
    *,
    width: int = 11,
    height: int = 11,
    spawn: Tuple[int, int] = (5, 5),
) -> WorldState:
    cfg = WorldConfig(width=width, height=height)
    agent = AgentBody(x=spawn[0], y=spawn[1])

    world_map = WorldMap.default(width=width, height=height)

    return WorldState(
        cfg=cfg,
        agent=agent,
        world_map=world_map,
    )