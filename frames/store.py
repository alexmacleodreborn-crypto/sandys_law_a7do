# sandys_law_a7do/frames/store.py

from typing import Optional
from .frame import Frame
from .fragment import Fragment

class FrameStore:
    def __init__(self):
        self.active: Optional[Frame] = None

    def open(self, frame: Frame):
        if self.active:
            raise RuntimeError("Frame already active")
        self.active = frame

    def add_fragment(self, fragment: Fragment):
        if not self.active:
            raise RuntimeError("No active frame")
        self.active.add(fragment)
    
    def close(self) -> Optional[Frame]:
        frame = self.active
        self.active = None
        return frame
        
    def observe_sensory(self, packets):
        for p in packets:
            if p.coherence >= 0.4:
                self.open(
                    kind="sensory",
                    data={
                        "modality": p.modality,
                        "region": p.body_region,
                        "coherence": p.coherence,
                },
            )
