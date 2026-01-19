from __future__ import annotations

from typing import List, Optional

from frames.frame import Frame


class FrameStore:
    """
    Holds active and completed frames.

    Doctrine:
    - No time
    - Frames are explicitly opened and closed
    - Only one active frame at a time (Phase 0–4)
    """

    def __init__(self) -> None:
        self.active: Optional[Frame] = None
        self.completed: List[Frame] = []

    def begin(self) -> Frame:
        if self.active is None:
            self.active = Frame()
        return self.active

    def add_fragment(self, fragment) -> None:
        if self.active is None:
            self.begin()
        self.active.add(fragment)

    def close(self) -> Optional[Frame]:
        if self.active is None:
            return None
        self.active.close()
        finished = self.active
        self.completed.append(finished)
        self.active = None
        return finished

    def recent(self, n: int = 10) -> List[Frame]:
        return self.completed[-n:]
