from __future__ import annotations
from typing import Iterable, List, Dict, Tuple

from .entry import LedgerEntry


class EmbodimentLedger:
    """
    Append-only ledger of embodied invariants.
    """

    def __init__(self) -> None:
        self._entries: List[LedgerEntry] = []

    def entries(self) -> Iterable[LedgerEntry]:
        return tuple(self._entries)

    def add(self, entry: LedgerEntry) -> None:
        self._entries.append(entry)

    def count(self) -> int:
        return len(self._entries)

    # --------------------------------------------
    # REQUIRED FOR CONSOLIDATION & SUMMARY
    # --------------------------------------------

    def _key(self, entry: LedgerEntry) -> Tuple:
        return (entry.kind, entry.regions, entry.conditions)

    def all_latest(self) -> Iterable[LedgerEntry]:
        """
        Return only the latest version of each invariant.
        """
        latest: Dict[Tuple, LedgerEntry] = {}

        for e in self._entries:
            key = self._key(e)
            if key not in latest or e.version > latest[key].version:
                latest[key] = e

        return tuple(latest.values())