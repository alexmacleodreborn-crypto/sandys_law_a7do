from __future__ import annotations
from typing import List
from embodiment.local.candidate import EmbodimentCandidate


class LocalEmbodimentBuffer:
    """
    Prebirth-local buffer for embodiment candidates.

    - No ledger writes
    - No consolidation
    - No promotion
    """

    def __init__(self) -> None:
        self._candidates: List[EmbodimentCandidate] = []

    def add(self, candidates: List[EmbodimentCandidate]) -> None:
        self._candidates.extend(candidates)

    def snapshot(self) -> List[EmbodimentCandidate]:
        return list(self._candidates)

    def clear(self) -> None:
        self._candidates.clear()