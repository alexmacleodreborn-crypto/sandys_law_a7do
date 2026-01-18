from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from world.world_state import WorldState


# ============================================================
# Phase 0: Space
# - Grid world
# - Deterministic adjacency
# - Boundary detection reports contact normals continuously
# ============================================================

Vec2 = Tuple[int, int]
Pos = Tuple[int, int]


@dataclass(frozen=True)
class ContactReport:
    """
    Reports structural contact at the agent's current position.
    Normals are integer unit vectors indicating where the blocking surface is.
    Example:
      (-1,0) means wall is on the LEFT of the agent (contact normal points leftward).
      (0,1) means wall is BELOW the agent.
    """
    contact: bool
    normals: List[Vec2]
    blocked_moves: List[Vec2]


class GridSpace:
    """
    Pure spatial logic: bounds + walls + contact evaluation.
    No physics, no sensors, no memory.
    """

    def __init__(self, state: WorldState) -> None:
        self.state = state

    # --------------------------------------------------------
    # Basic bounds
    # --------------------------------------------------------

    def in_bounds(self, p: Pos) -> bool:
        return self.state.in_bounds(p[0], p[1])

    def neighbors4(self, p: Pos) -> List[Tuple[Vec2, Pos]]:
        """
        Returns 4-neighborhood as (delta, neighbor_pos).
        Ordering is deterministic: Up, Down, Left, Right.
        """
        x, y = p
        return [
            ((0, -1), (x, y - 1)),  # up
            ((0,  1), (x, y + 1)),  # down
            ((-1, 0), (x - 1, y)),  # left
            ((1,  0), (x + 1, y)),  # right
        ]

    # --------------------------------------------------------
    # Walls and blocking
    # --------------------------------------------------------

    def is_blocked_move(self, a: Pos, b: Pos) -> bool:
        """
        A move is blocked if:
        - destination is out of bounds (world boundary is a hard wall)
        - OR an explicit wall exists between a and b
        """
        if not self.in_bounds(b):
            return True
        if self.state.has_wall_between(a, b):
            return True
        return False

    # --------------------------------------------------------
    # Contact detection (the key requirement)
    # --------------------------------------------------------

    def contact_at(self, p: Pos) -> ContactReport:
        """
        Detects whether the agent is in contact with any boundary/wall surfaces.

        In a grid world, "touching a wall" means that at least one adjacent move is blocked.

        This yields continuous wall detection:
        - if you walk along a wall, blocked moves keep appearing every step
        - not only at corners.
        """
        normals: List[Vec2] = []
        blocked: List[Vec2] = []

        for d, nb in self.neighbors4(p):
            if self.is_blocked_move(p, nb):
                blocked.append(d)

                # Normal is the direction toward the wall surface.
                # If moving (1,0) is blocked, wall is to the RIGHT, so normal is (1,0).
                normals.append(d)

        # Deduplicate while preserving deterministic order
        normals = self._dedupe(normals)
        blocked = self._dedupe(blocked)

        return ContactReport(
            contact=len(normals) > 0,
            normals=normals,
            blocked_moves=blocked,
        )

    # --------------------------------------------------------
    # Deterministic dedupe
    # --------------------------------------------------------

    @staticmethod
    def _dedupe(vs: List[Vec2]) -> List[Vec2]:
        out: List[Vec2] = []
        seen = set()
        for v in vs:
            if v not in seen:
                seen.add(v)
                out.append(v)
        return out

    # --------------------------------------------------------
    # Move validation helper
    # --------------------------------------------------------

    def validate_move(self, p: Pos, d: Vec2) -> Tuple[bool, Pos, Optional[str]]:
        """
        Checks whether moving by delta d is possible.
        Returns: (ok, new_pos, reason)
        """
        x, y = p
        dx, dy = d
        nxt = (x + dx, y + dy)

        if self.is_blocked_move(p, nxt):
            if not self.in_bounds(nxt):
                return (False, p, "blocked_by_boundary")
            return (False, p, "blocked_by_wall")

        return (True, nxt, None)
