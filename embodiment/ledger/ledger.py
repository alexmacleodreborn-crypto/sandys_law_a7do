# embodiment/ledger/ledger.py

from __future__ import annotations
from typing import Iterable, List

from .entry import LedgerEntry


class EmbodimentLedger:
    """
    Append-only ledger of embodied invariants.

    This is NOT memory.
    This is NOT belief.
    This is the substrate of identity.
    """

    def __init__(self) -> None:
        self._entries: List[LedgerEntry] = []

    def entries(self) -> Iterable[LedgerEntry]:
        return tuple(self._entries)

    def add(self, entry: LedgerEntry) -> None:
        """
        Add a new embodied invariant.
        No deletion. No overwrite.
        """
        self._entries.append(entry)

    def count(self) -> int:
        return len(self._entries)