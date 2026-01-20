# sandys_law_a7do/memory/structural_memory.py

from typing import List
from .trace import MemoryTrace


class StructuralMemory:
    """
    StructuralMemory stores crystallised structural traces.

    This is NOT a reward store.
    This is NOT a policy memory.
    It only persists structure that survives stability gates.
    """

    def __init__(self):
        # Internal crystallised structures
        self._structures: List[MemoryTrace] = []

        # Pending traces before crystallisation
        self._buffer: List[MemoryTrace] = []

    # --------------------------------------------------
    # Trace ingestion
    # --------------------------------------------------

    def add_trace(self, trace: MemoryTrace) -> None:
        """
        Add a trace to the pending buffer.
        """
        self._buffer.append(trace)

    # --------------------------------------------------
    # Crystallisation
    # --------------------------------------------------

    def crystallize(self) -> None:
        """
        Promote buffered traces into long-term memory.
        """
        if not self._buffer:
            return

        self._structures.extend(self._buffer)
        self._buffer.clear()

    # --------------------------------------------------
    # Decay
    # --------------------------------------------------

    def decay(self, factor: float = 0.5) -> None:
        """
        Apply decay to memory.

        factor in (0,1):
          - 1.0 = no decay
          - 0.0 = full wipe
        """
        if factor <= 0.0:
            self._structures.clear()
        elif factor < 1.0:
            keep = int(len(self._structures) * factor)
            self._structures = self._structures[:keep]

        # Always clear buffer on decay
        self._buffer.clear()

    # --------------------------------------------------
    # Public API (THIS IS WHAT BOOTSTRAP USES)
    # --------------------------------------------------

    def count(self) -> int:
        """
        Number of crystallised memory structures.
        """
        return len(self._structures)

    def all(self) -> List[MemoryTrace]:
        """
        Read-only access to crystallised memory.
        """
        return list(self._structures)