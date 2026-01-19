# sandys_law_a7do/memory/trace.py

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class MemoryTrace:
    """
    Atomic memory unit.
    Immutable record of an experience.
    """
    trace_id: int
    features: Dict[str, Any]
    weight: float = 1.0
    tags: List[str] = field(default_factory=list)

    def reinforce(self, amount: float):
        self.weight += amount

    def decay(self, factor: float):
        self.weight *= factor
