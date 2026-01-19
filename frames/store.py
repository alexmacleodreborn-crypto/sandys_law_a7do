from __future__ import annotations

from typing import Optional

from .frame import Frame
from .fragment import Fragment


class FrameStore:
    """
    Manages the active frame and closed frames.

    Guarantees:
    - Only one active frame at a time
    - Frames are immutable once closed
    """

    def __init__(self) -> None:
        self.active: Optional[Frame] = None

    # --------------------------------------------------
    # Frame lifecycle
    # --------------------------------------------------

    def begin(self) -> Frame:
        if self.active and not self.active.closed:
            raise RuntimeError("Cannot begin a new frame while one is active")
        self.active = Frame()
        return self.active

    def add_fragment(self, fragment: Fragment) -> None:
        if not self.active:
            raise RuntimeError("No active frame to add fragment to")
        self.active.add(fragment)

    def close(self) -> Optional[Frame]:
        if not self.active:
            return None

        frame = self.active
        frame.close()
        self.active = None
        return frame
