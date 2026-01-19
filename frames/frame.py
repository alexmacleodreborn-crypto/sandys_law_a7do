from __future__ import annotations
from dataclasses import dataclass, field
from typing import List
from uuid import uuid4

from frames.fragment import Fragment
from frames.frame_store import FrameStore


@dataclass
class Frame:
    """
    A bounded information episode.

    This replaces time.
    """
    id: str = field(default_factory=lambda: uuid4().hex)
    fragments: List[Fragment] = field(default_factory=list)
    closed: bool = False

    def add(self, fragment: Fragment) -> None:
        if self.closed:
            raise RuntimeError("Cannot add fragment to closed frame")
        self.fragments.append(fragment)

    def close(self) -> None:
        """
        Marks the end of the frame.
        """
        self.closed = True

    def is_empty(self) -> bool:
        return len(self.fragments) == 0
