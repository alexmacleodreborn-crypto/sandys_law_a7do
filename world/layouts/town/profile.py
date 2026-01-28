from dataclasses import dataclass


@dataclass(frozen=True)
class TownProfile:
    name: str
    population: int
    base_temperature: float
    base_noise: float
    season: str


def make_default_town() -> TownProfile:
    return TownProfile(
        name="OriginTown",
        population=1200,
        base_temperature=0.2,
        base_noise=0.15,
        season="spring",
    )