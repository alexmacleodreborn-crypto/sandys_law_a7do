# embodiment/consolidation/ledger.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Iterable

from embodiment.ledger.entry import LedgerEntry


# ============================================================
# Embodiment Ledger
#
# The Ledger is the ONLY structure allowed to persist
# grounded embodied invariants.
#
# Properties:
# - append-only (history preserved)
# - versioned per entry
# - conservative (no deletion, no overwrite)
# - auditable
#
# No subsystem mutates entries in place.
# ============================================================


@dataclass
class EmbodimentLedger:
    """
    Append-only store of embodied invariants.

    Entries are grouped by (kind, regions, conditions).
    Each group forms a versioned chain.
    """

    _entries: Dict[str, List[LedgerEntry]] = field(default_factory=dict)

    # --------------------------------------------------------
    # Internal keying
    # --------------------------------------------------------

    @staticmethod
    def _key(entry: LedgerEntry) -> str:
        """
        Deterministic identity key for an invariant chain.
        """
        regions = ",".join(sorted(entry.regions))
        conditions = "|".join(entry.conditions)
        return f"{entry.kind}:{regions}:{conditions}"

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def add(self, entry: LedgerEntry) -> None:
        """
        Append a new ledger entry.

        This NEVER replaces existing entries.
        """
        key = self._key(entry)
        self._entries.setdefault(key, []).append(entry)

    def latest(self, key: str) -> LedgerEntry | None:
        """
        Return the most recent version of an entry chain.
        """
        chain = self._entries.get(key)
        if not chain:
            return None
        return chain[-1]

    def all_latest(self) -> List[LedgerEntry]:
        """
        Return the latest entry from each invariant chain.
        """
        return [chain[-1] for chain in self._entries.values() if chain]

    def history(self, key: str) -> List[LedgerEntry]:
        """
        Return full version history for a given invariant key.
        """
        return list(self._entries.get(key, []))

    def __len__(self) -> int:
        """
        Number of distinct invariant chains.
        """
        return len(self._entries)

    # --------------------------------------------------------
    # Introspection / audit
    # --------------------------------------------------------

    def audit(self) -> Dict[str, int]:
        """
        Returns a summary useful for debugging / inspection.
        """
        return {
            key: len(chain)
            for key, chain in self._entries.items()
        }

    def iter_entries(self) -> Iterable[LedgerEntry]:
        """
        Iterate over ALL entries (all versions).
        """
        for chain in self._entries.values():
            for entry in chain:
                yield entry