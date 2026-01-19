from __future__ import annotations

from typing import Optional

from .frame import Frame
from .fragment import Fragment


class FrameStore:
    """
    Manages active and closed frames.
    """

    def __init__(self) -> None:
        self.active: Optional[Frame] = None

    def begin(self) -> Frame:
        if self.active and not self.active.closed:
            raise RuntimeError("Active frame already exists")
        self.active = Frame()
        return self.active

    def add_fragment(self, fragment: Fragment) -> None:
        if not self.active:
            raise RuntimeError("No active frame")
        self.active.add(fragment)

    def close(self) -> Optional[Frame]:
        if not self.active:
            return None
        frame = self.active
        frame.close()
        self.active = None
        return frame
