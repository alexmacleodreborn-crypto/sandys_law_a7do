from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

from world.layouts.town.profile import TownProfile


# ============================================================
# ENVIRONMENT CELL
# ============================================================

@dataclass(frozen=True)
class EnvironmentCell:
    temperature: float = 0.0
    noise: float = 0.0
    light: float = 0.0


# ============================================================
# WORLD MAP (2D PHYSICAL LAYOUT)
# ============================================================

class WorldMap:
    """
    Physical environment grid.
    No semantics. No memory. Deterministic.
    """

    def __init__(
        self,
        *,
        width: int,
        height: int,
        town: TownProfile,
        cells: Dict[Tuple[int, int], EnvironmentCell],
    ) -> None:
        self.width = width
        self.height = height
        self.town = town
        self._cells = cells

    # --------------------------------------------------------
    # REQUIRED CONSTRUCTOR ✅
    # --------------------------------------------------------

    @classmethod
    def default(cls, *, width: int, height: int) -> "WorldMap":
        """
        Minimal valid world map.
        Used at birth / Phase 0.
        """
        town = TownProfile.default()

        cells: Dict[Tuple[int, int], EnvironmentCell] = {}

        for x in range(width):
            for y in range(height):
                cells[(x, y)] = EnvironmentCell(
                    temperature=town.base_temperature,
                    noise=0.0,
                    light=0.0,
                )

        return cls(
            width=width,
            height=height,
            town=town,
            cells=cells,
        )

    # --------------------------------------------------------
    # ENVIRONMENT ACCESS
    # --------------------------------------------------------

    def environment_at(self, x: int, y: int) -> EnvironmentCell:
        return self._cells.get((x, y), EnvironmentCell())