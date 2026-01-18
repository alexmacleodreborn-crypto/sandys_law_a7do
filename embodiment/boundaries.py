from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple


@dataclass(frozen=True)
class Boundary:
    """
    A physical boundary of the body.

    Used to detect contact with the world.
    """
    region: str
    min_xy: Tuple[int, int]
    max_xy: Tuple[int, int]

    def contains(self, x: int, y: int) -> bool:
        return (
            self.min_xy[0] <= x <= self.max_xy[0]
            and self.min_xy[1] <= y <= self.max_xy[1]
        )


class BoundaryMap:
    """
    Collection of all body boundaries.
    """

    def __init__(self) -> None:
        self._boundaries: list[Boundary] = []

    def add(self, boundary: Boundary) -> None:
        self._boundaries.append(boundary)

    def detect_contact(self, x: int, y: int) -> list[str]:
        """
        Returns body regions contacted at (x, y).
        """
        return [b.region for b in self._boundaries if b.contains(x, y)]
