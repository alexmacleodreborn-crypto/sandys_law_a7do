from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sandys_law_a7do.integration.phase1_loop import Phase1Loop, Phase1Entry, PreferenceUpdate
from sandys_law_a7do.frames_toggle_types import FrameLike  # optional shim (see note)


# ============================================================
# Phase 2 Memory Trace
# ============================================================

@dataclass(frozen=True)
class MemoryTrace:
    signature: str
    strength: float
    frames_observed: int


class StructuralMemory:
    """
    Minimal crystallizing memory:
    - increases strength when a signature repeats
    - does not store semantics
    """

    def __init__(self) -> None:
        self._db: Dict[str, Tuple[float, int]] = {}  # sig -> (strength, frames)

    def observe(self, entry: Phase1Entry) -> MemoryTrace:
        old_strength, old_frames = self._db.get(entry.signature, (0.0, 0))

        # strengthen on coherence, weaken on fragmentation + high error
        delta = (0.10 * entry.coherence) - (0.06 * entry.fragmentation) - (0.08 * min(1.0, entry.prediction_error_l1))
        new_strength = max(0.0, min(1.0, old_strength + delta))

        new_frames = old_frames + 1
        self._db[entry.signature] = (new_strength, new_frames)

        return MemoryTrace(signature=entry.signature, strength=new_strength, frames_observed=new_frames)

    def traces(self) -> List[MemoryTrace]:
        out: List[MemoryTrace] = []
        for sig in sorted(self._db.keys()):
            s, n = self._db[sig]
            out.append(MemoryTrace(signature=sig, strength=float(s), frames_observed=int(n)))
        return out


# ============================================================
# Phase 2 Loop
# ============================================================

class Phase2Loop:
    """
    Phase 2 = Phase 1 + Memory crystallization.

    Returns:
      entry (Phase1Entry)
      pref_update (PreferenceUpdate|None)
      trace (MemoryTrace)
    """

    def __init__(self) -> None:
        self.phase1 = Phase1Loop()
        self.memory = StructuralMemory()

    def step(self, *, frames: List[FrameLike]) -> Tuple[Phase1Entry, Optional[PreferenceUpdate], MemoryTrace]:
        entry, pref_update = self.phase1.step(frames=frames)
        trace = self.memory.observe(entry)
        return entry, pref_update, trace
