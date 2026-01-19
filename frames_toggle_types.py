from __future__ import annotations
from typing import Protocol, Dict, Any


class FragmentLike(Protocol):
    source: str
    kind: str
    payload: Dict[str, Any]


class FrameLike(Protocol):
    fragments: list[FragmentLike]
