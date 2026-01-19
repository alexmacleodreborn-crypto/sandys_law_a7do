from __future__ import annotations

from typing import List
from sandys_law_a7do.memory.trace import MemoryTrace


class StructuralMemory:
    """
    Structural memory (Phase 2).

    This stores invariant patterns extracted from frames.
    No time, no reward, no semantics.
    """

    def __init__(self) -> None:
        self._traces: List[MemoryTrace] = []

    # --------------------------------------------------------

    def integrate(
        self,
        *,
        frames: List,
        coherence: float,
        fragmentation: float,
    ) -> MemoryTrace:
        """
        Integrate a closed frame into memory.
        """
        trace = MemoryTrace.from_frames(
            frames=frames,
            coherence=coherence,
            fragmentation=fragmentation,
        )

        self._merge(trace)
        return trace

    # --------------------------------------------------------

    def _merge(self, new_trace: MemoryTrace) -> None:
        """
        Merge trace if signature already exists.
        """
        for t in self._traces:
            if t.signature == new_trace.signature:
                t.merge(new_trace)
                return

        self._traces.append(new_trace)

    # --------------------------------------------------------

    def traces(self) -> List[MemoryTrace]:
        """
        Read-only access for dashboards.
        """
        return list(self._traces)
