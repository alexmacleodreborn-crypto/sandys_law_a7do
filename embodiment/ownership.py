from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class OwnershipEvent:
    region: str
    owned: bool


class OwnershipResolver:
    """
    Resolves whether a sensation belongs to this body.
    """

    def __init__(self, known_regions: set[str]) -> None:
        self.known_regions = known_regions

    def resolve(self, region: str) -> OwnershipEvent:
        return OwnershipEvent(
            region=region,
            owned=region in self.known_regions
        )
