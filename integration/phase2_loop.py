from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sandys_law_a7do.integration.phase1_loop import (
    Phase1Loop,
    Phase1Entry,
    PreferenceUpdate,
)


# ============================================================
# Memory Trace
# ============================================================

@dataclass(frozen=True)
class MemoryTrace:
    signature: str
    strength: float
    frames_observed: int


class StructuralMemory:
    """
    Crystallizes repeated structure.
    """

    def __init__(self) -> None:
        self._store: Dict[str, Tuple[float, int]] = {}

    def observe(self, entry: Phase1Entry) -> MemoryTrace:
        old_strength, old_n = self._store.get(entry.signature, (0.0, 0))

        delta = (0.15 * entry.coherence) - (0.1 * entry.prediction_error_l1)
        new_strength = max(0.0, min(1.0, old_strength + delta))
        new_n = old_n + 1

        self._store[entry.signature] = (new_strength, new_n)

        return MemoryTrace(
            signature=entry.signature,
            strength=float(new_strength),
            frames_observed=new_n,
        )

    def traces(self) -> List[MemoryTrace]:
        return [
            MemoryTrace(sig, s, n)
            for sig, (s, n) in self._store.items()
        ]


# ============================================================
# Phase 2 Loop
# ============================================================

class Phase2Loop:
    """
    Phase 2 = Phase 1 + Structural Memory
    """

    def __init__(self) -> None:
        self.phase1 = Phase1Loop()
        self.memory = StructuralMemory()

    def step(self, *, frames: List[object]) -> Tuple[Phase1Entry, Optional[PreferenceUpdate], MemoryTrace]:
        entry, pref = self.phase1.step(frames=frames)
        trace = self.memory.observe(entry)
        return entry, pref, trace
