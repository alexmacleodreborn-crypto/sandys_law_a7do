from __future__ import annotations

import json
from pathlib import Path

from .record import IdentityRecord


class IdentityStore:
    """
    Persistence for identity continuity.
    """

    def __init__(self, path: str):
        self.path = Path(path)

    def load(self) -> IdentityRecord:
        if not self.path.exists():
            return IdentityRecord()

        with self.path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        return IdentityRecord(
            identity_id=data.get("identity_id"),
            coherence=data.get("coherence", 0.0),
            fragmentation=data.get("fragmentation", 1.0),
            confidence=data.get("confidence", 0.0),
            traits=data.get("traits", {}),
        )

    def save(self, identity: IdentityRecord) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(identity.to_dict(), f, indent=2)
