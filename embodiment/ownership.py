# sandys_law_a7do/embodiment/ownership.py

from dataclasses import dataclass, field
from typing import Set


@dataclass
class OwnershipMap:
    """
    Tracks which entities are considered part of self.
    """
    owned_entities: Set[str] = field(default_factory=set)

    def claim(self, entity_id: str) -> None:
        self.owned_entities.add(entity_id)

    def release(self, entity_id: str) -> None:
        self.owned_entities.discard(entity_id)

    def is_owned(self, entity_id: str) -> bool:
        return entity_id in self.owned_entities
