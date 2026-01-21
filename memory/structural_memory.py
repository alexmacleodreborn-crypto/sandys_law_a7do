# sandys_law_a7do/memory/structural_memory.py

from typing import List
from .trace import MemoryTrace


class StructuralMemory:
    """
    Regulated long-term memory store.

    - trace_log : all experienced traces (attempted memory)
    - traces    : consolidated / crystallised memory only
    """

    def __init__(self):
        self.traces: List[MemoryTrace] = []
        self.trace_log: List[MemoryTrace] = []   # ✅ NEW (do not remove)

    # --------------------------------------------------
    # CONSOLIDATED MEMORY ONLY
    # --------------------------------------------------
    def add_trace(self, trace: MemoryTrace):
        self.traces.append(trace)

    def count(self) -> int:
        return len(self.traces)

    # --------------------------------------------------
    # DEBUG / INSPECTION HELPERS (SAFE)
    # --------------------------------------------------
    def all_traces(self) -> List[MemoryTrace]:
        return self.traces

    def recent_attempts(self, n: int = 10) -> List[MemoryTrace]:
        return self.trace_log[-n:]