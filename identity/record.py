from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any
from uuid import uuid4


@dataclass(frozen=True)
class IdentityRecord:
    """
    Persistent continuity of the agent.
    """
    identity_id: str = field(default_factory=lambda: uuid4().hex)
    coherence: float = 0.0
    fragmentation: float = 1.0
    confidence: float = 0.0

    traits: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "identity_id": self.identity_id,
            "coherence": self.coherence,
            "fragmentation": self.fragmentation,
            "confidence": self.confidence,
            "traits": dict(self.traits),
        }
