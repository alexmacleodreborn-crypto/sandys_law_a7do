from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict
from uuid import uuid4


@dataclass(frozen=True)
class Fragment:
    """
    Atomic unit of information inside a Frame.

    - No time
    - No semantics
    - Just structured occurrence
    """
    id: str = field(default_factory=lambda: uuid4().hex)
    source: str = "unknown"
    kind: str = "unknown"
    payload: Dict[str, Any] = field(default_factory=dict)

