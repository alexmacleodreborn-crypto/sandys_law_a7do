from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class Place:
    name: str
    temperature_offset: float
    noise_level: float


def make_default_places() -> Dict[str, Place]:
    return {
        "hospital": Place(
            name="hospital",
            temperature_offset=0.1,
            noise_level=0.25,
        ),
        "home": Place(
            name="home",
            temperature_offset=0.0,
            noise_level=0.05,
        ),
        "park": Place(
            name="park",
            temperature_offset=-0.05,
            noise_level=0.2,
        ),
    }