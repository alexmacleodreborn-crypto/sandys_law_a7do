# sandys_law_a7do/memory/trace.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class MemoryTrace:
    """
    Atomic structural memory unit.

    This is NOT semantic memory.
    This is NOT reward memory.
    It records only structural conditions that passed stability gates.
    """

    tick: int
    Z: float
    coherence: float
    stability: float
    frame_signature: str

    weight: float = 1.0
    tags: List[str] = field(default_factory=list)

    # --------------------------------------------------
    # Reinforcement / decay (optional, future use)
    # --------------------------------------------------

    def reinforce(self, amount: float = 0.1):
        self.weight += amount

    def decay(self, factor: float = 0.9):
        self.weight *= factor