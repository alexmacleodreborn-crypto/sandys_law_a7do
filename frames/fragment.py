from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class Fragment:
    """
    Smallest unit of information.

    A fragment does NOT imply meaning.
    It is just a structured change.
    """
    source: str                 # e.g. "world", "sensor", "body"
    kind: str                   # e.g. "contact", "thermal", "move"
    payload: Dict[str, Any]     # raw data only
