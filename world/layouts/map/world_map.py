# world/layouts/map/world_map.py

from dataclasses import dataclass
from typing import Dict, Tuple, List

from world.layouts.town.profile import TownProfile
from world.layouts.places.core_places import Place


# ============================================================
# WORLD MAP (Phase 0)
# ------------------------------------------------------------
# A pure spatial field:
# - deterministic
# - query-only
# - no agents
# - no memory
# ============================================================


@dataclass
class CellEnvironment:
    """
    Environment values at a single coordinate.
    """
    temperature: float
    noise: float


class WorldMap:
    """
    Static 2D spatial map combining:
    - Town baseline
    - Place influences
    """

    def __init__(
        self,
        *,
        town: TownProfile,
        places: Dict[str, Place],
        width: int,
        height: int,
    ) -> None:
        self.town = town
        self.places = places
        self.width = width
        self.height = height

    # --------------------------------------------------------
    # Core query
    # --------------------------------------------------------

    def environment_at(self, x: int, y: int) -> CellEnvironment:
        """
        Return environment values at a grid coordinate.
        """

        # Base from town
        temperature = self.town.base_temperature
        noise = self.town.base_noise

        # Add place influences
        for place in self.places.values():
            if self._in_radius(x, y, place):
                temperature += place.temperature_delta
                noise += place.noise_delta

        return CellEnvironment(
            temperature=round(temperature, 3),
            noise=round(noise, 3),
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _in_radius(x: int, y: int, place: Place) -> bool:
        px, py = place.center
        return abs(px - x) + abs(py - y) <= place.radius