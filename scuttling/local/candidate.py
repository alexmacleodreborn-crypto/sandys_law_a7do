from __future__ import annotations
from typing import List

from embodiment.local.candidate import EmbodimentCandidate
from embodiment.local.builder import CandidateBuilder


class LocalEmbodimentCandidates:
    """
    Local (pre-embodiment) candidate store.

    Doctrine:
    - NOT embodiment
    - NOT identity
    - NOT consolidated
    - purely structural, local-first
    """

    def __init__(self) -> None:
        self._builder = CandidateBuilder()
        self._candidates: List[EmbodimentCandidate] = []

    def ingest_coupling_snapshot(
        self,
        *,
        snapshot: dict,
        support: int,
    ) -> None:
        new = self._builder.build_from_coupling(
            snapshot=snapshot,
            support=support,
        )
        self._candidates.extend(new)

    def snapshot(self) -> List[dict]:
        return [
            {
                "kind": c.kind,
                "regions": list(c.regions),
                "support": c.support,
                "stability": round(c.stability, 3),
                "confidence_hint": round(c.confidence_hint, 3),
            }
            for c in self._candidates
        ]