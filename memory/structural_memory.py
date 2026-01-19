# sandys_law_a7do/memory/structural_memory.py

from typing import List
from .trace import MemoryTrace
from .decay import decay_weight


class StructuralMemory:
    """
    Holds all memory traces.
    Responsible for retention and decay, not interpretation.
    """

    def __init__(self):
        self.traces: List[MemoryTrace] = []
        self._next_id = 0

    def add_trace(self, features: dict, tags=None) -> MemoryTrace:
        trace = MemoryTrace(
            trace_id=self._next_id,
            features=features,
            tags=tags or []
        )
        self._next_id += 1
        self.traces.append(trace)
        return trace

    def apply_decay(self, rate: float):
        for trace in self.traces:
            trace.decay(decay_weight(rate))

    def active_traces(self, threshold: float = 0.05) -> List[MemoryTrace]:
        return [t for t in self.traces if t.weight >= threshold]
