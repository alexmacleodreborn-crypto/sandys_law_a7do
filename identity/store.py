from __future__ import annotations

import json
import os
from dataclasses import replace
from typing import Optional
from uuid import uuid4

from identity.record import IdentityRecord


class IdentityStore:
    """
    Minimal persistence for IdentityRecord.

    Doctrine:
    - Identity is append-safe (overwrites are allowed only as version bumps)
    - No deletion required
    """

    def __init__(self, path: str = "data/identity/identity.json") -> None:
        self.path = path
        os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

    def exists(self) -> bool:
        return os.path.exists(self.path)

    def load(self) -> IdentityRecord:
        if not self.exists():
            return self._create_new()

        with open(self.path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return IdentityRecord(
            identity_id=str(data["identity_id"]),
            genesis_id=str(data["genesis_id"]),
            incarnation=int(data["incarnation"]),
            continuity_version=int(data.get("continuity_version", 1)),
            stability_index=float(data.get("stability_index", 0.10)),
            novelty_index=float(data.get("novelty_index", 0.10)),
            embodiment_integrity=float(data.get("embodiment_integrity", 0.10)),
            commitments=list(data.get("commitments", [])),
        )

    def save(self, record: IdentityRecord) -> None:
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(record.to_dict(), f, ensure_ascii=False, indent=2)

    def bump(self, record: IdentityRecord, *, reason: str) -> IdentityRecord:
        """
        Explicit continuity bump.
        """
        new = replace(record, continuity_version=int(record.continuity_version) + 1)
        # (We intentionally do not store 'reason' inside identity; reasons live in event/ledger layers.)
        return new

    # -------------------------
    # Internal
    # -------------------------

    def _create_new(self) -> IdentityRecord:
        record = IdentityRecord(
            identity_id=uuid4().hex,
            genesis_id=uuid4().hex,
            incarnation=1,
            continuity_version=1,
            stability_index=0.10,
            novelty_index=0.10,
            embodiment_integrity=0.10,
            commitments=[],
        )
        self.save(record)
        return record