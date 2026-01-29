from __future__ import annotations
from typing import List

from scuttling.reflex_types import ReflexResult
from scuttling.coupling.reflex_coupling import ReflexCouplingEngine


class ReflexBuffer:
    """
    Collects reflex results within a single tick before coupling.
    """

    def __init__(self) -> None:
        self._buffer: List[ReflexResult] = []
        self._coupler = ReflexCouplingEngine()

    def push(self, result: ReflexResult) -> None:
        if result.triggered:
            self._buffer.append(result)

    def resolve(self):
        outcome = self._coupler.couple(results=self._buffer)
        self._buffer.clear()
        return outcome