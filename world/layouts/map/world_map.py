from dataclasses import dataclass
from typing import Dict, Tuple

from layouts.town.profile import TownProfile
from layouts.places.core_places import Place


@dataclass(frozen=True)
class EnvironmentSample:
    temperature: float
    noise: float


class WorldMap:
    """
    Combines town baseline + local place influence.
    """

    def __init__(
        self,
        *,
        town: TownProfile,
        places: Dict[str, Place],
        width: int,
        height: int,
    ):
        self.town = town
        self.places = places
        self.width = width
        self.height = height

        # Simple deterministic placement
        self.place_map: Dict[Tuple[int, int], str] = {
            (5, 5): "home",
            (2, 2): "hospital",
            (8, 8): "park",
        }

    def environment_at(self, x: int, y: int) -> EnvironmentSample:
        place_name = self.place_map.get((x, y))
        place = self.places.get(place_name)

        temp = self.town.base_temperature
        noise = self.town.base_noise

        if place:
            temp += place.temperature_offset
            noise += place.noise_level

        return EnvironmentSample(
            temperature=round(temp, 3),
            noise=round(noise, 3),
        )