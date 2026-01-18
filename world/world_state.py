from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


# ============================================================
# Phase 0 Doctrine: World is pure physics + events
# - No time
# - No memory
# - No semantics
# - Deterministic ordering
# ============================================================


class WorldEventType(str, Enum):
    OBSERVATION = "observation"
    ACTION = "action"
    OUTCOME = "outcome"
    SYSTEM = "system"


@dataclass(frozen=True)
class WorldEvent:
    """
    World-only event. Deterministic IDs are generated from an incrementing counter
    in WorldState (NOT uuid), so replay is stable across identical action sequences.
    """
    event_id: str
    type: WorldEventType
    name: str
    payload: Dict[str, Any]
    parent_id: Optional[str] = None


@dataclass
class AgentBody:
    """
    Minimal embodied body placeholder (Phase 0).
    - position is in grid coordinates
    - effort is an actuator scalar (fixed for now)
    """
    x: int
    y: int
    effort: float = 1.0

    # Simple local sensor state
    contact: bool = False
    contact_normals: List[Tuple[int, int]] = field(default_factory=list)  # e.g. [(-1,0)] if wall on left
    thermal: float = 0.0   # only meaningful when contact=True (enforced in sensors)
    pain: float = 0.0      # only meaningful when overload=True


@dataclass
class WorldConfig:
    """
    World tunables (Phase 0 only).
    Keep this conservative and deterministic.
    """
    width: int = 11
    height: int = 11

    # Thermal / pain
    ambient_temp: float = 0.0
    contact_temp_gain: float = 0.6      # how strongly surface temperature affects thermal
    pain_threshold: float = 0.85        # pain if overload exceeds this

    # Physics
    move_cost: float = 0.10             # effort cost per successful move
    block_cost: float = 0.20            # effort cost when blocked by wall


@dataclass
class WorldState:
    """
    The entire world state (Phase 0).
    Deterministic and serializable.
    """
    cfg: WorldConfig
    agent: AgentBody

    # Walls are stored as blocked edges between adjacent cells.
    # Each wall is an undirected edge represented by ordered endpoints:
    # ((x1,y1),(x2,y2)) with lexicographic ordering to keep canonical.
    walls: Set[Tuple[Tuple[int, int], Tuple[int, int]]] = field(default_factory=set)

    # Surface temperature map per cell (simple scalar field)
    # If absent, ambient_temp is assumed.
    cell_temp: Dict[Tuple[int, int], float] = field(default_factory=dict)

    # Deterministic event counter
    _event_counter: int = 0

    # --------------------------------------------------------
    # Event utilities
    # --------------------------------------------------------

    def next_event_id(self, prefix: str = "w") -> str:
        self._event_counter += 1
        return f"{prefix}{self._event_counter:08d}"

    def emit(self, type: WorldEventType, name: str, payload: Dict[str, Any], parent_id: Optional[str] = None) -> WorldEvent:
        return WorldEvent(
            event_id=self.next_event_id(),
            type=type,
            name=name,
            payload=payload,
            parent_id=parent_id,
        )

    # --------------------------------------------------------
    # Canonical wall representation helpers
    # --------------------------------------------------------

    @staticmethod
    def _canon_edge(a: Tuple[int, int], b: Tuple[int, int]) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        return (a, b) if a <= b else (b, a)

    def add_wall_between(self, a: Tuple[int, int], b: Tuple[int, int]) -> None:
        self.walls.add(self._canon_edge(a, b))

    def has_wall_between(self, a: Tuple[int, int], b: Tuple[int, int]) -> bool:
        return self._canon_edge(a, b) in self.walls

    # --------------------------------------------------------
    # Bounds
    # --------------------------------------------------------

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cfg.width and 0 <= y < self.cfg.height

    def clamp_in_bounds(self, x: int, y: int) -> Tuple[int, int]:
        return (max(0, min(self.cfg.width - 1, x)), max(0, min(self.cfg.height - 1, y)))

    # --------------------------------------------------------
    # Temperature field
    # --------------------------------------------------------

    def temp_at(self, x: int, y: int) -> float:
        return float(self.cell_temp.get((x, y), self.cfg.ambient_temp))

    # --------------------------------------------------------
    # Snapshot (for dashboards/tests)
    # --------------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        return {
            "cfg": {
                "width": self.cfg.width,
                "height": self.cfg.height,
                "ambient_temp": self.cfg.ambient_temp,
                "contact_temp_gain": self.cfg.contact_temp_gain,
                "pain_threshold": self.cfg.pain_threshold,
                "move_cost": self.cfg.move_cost,
                "block_cost": self.cfg.block_cost,
            },
            "agent": {
                "x": self.agent.x,
                "y": self.agent.y,
                "effort": self.agent.effort,
                "contact": self.agent.contact,
                "contact_normals": list(self.agent.contact_normals),
                "thermal": self.agent.thermal,
                "pain": self.agent.pain,
            },
            "walls_count": len(self.walls),
            "event_counter": self._event_counter,
        }


# ------------------------------------------------------------
# Convenience constructor for Phase 0 demos
# ------------------------------------------------------------

def make_default_world(
    *,
    width: int = 11,
    height: int = 11,
    spawn: Tuple[int, int] = (5, 5),
) -> WorldState:
    cfg = WorldConfig(width=width, height=height)
    agent = AgentBody(x=spawn[0], y=spawn[1])

    ws = WorldState(cfg=cfg, agent=agent)

    # Build outer boundary walls so the agent can't leave the world.
    # We encode boundary walls as blocked edges between in-bounds cell and "virtual" out-of-bounds neighbor,
    # but since we only store in-bounds edges, we represent boundaries by blocking motion that would exit.
    # This will be handled in space/physics step logic; still, we pre-create internal perimeter walls too:
    # (optional) leave empty here; boundaries will be treated as hard walls by bounds checks.

    return ws
