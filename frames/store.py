# sandys_law_a7do/frames/store.py

from typing import Any, Dict, List, Optional
from sensory.wall import SensoryPacket


class FrameStore:
    """
    Frame Store

    Responsibilities:
    - Observe pre-semantic sensory packets
    - Open frames ONLY when coherence threshold is crossed
    - Store frames as internal data (dicts)
    - NO learning
    - NO semantics
    - NO mutation of packets
    """

    def __init__(self) -> None:
        self.frames: List[Dict[str, Any]] = []
        self.active: Optional[Dict[str, Any]] = None

    # --------------------------------------------------
    # SENSORY OBSERVATION
    # --------------------------------------------------

    def observe_sensory(self, packets: List[SensoryPacket]) -> None:
        """
        Observe degraded sensory packets.

        Frames open ONLY when packet coherence is sufficient.
        """

        for p in packets:
            # HARD SAFETY GUARD — never crash on bad data
            if not isinstance(p, SensoryPacket):
                continue

            # Coherence gate (pre-semantic)
            if p.coherence < 0.4:
                continue

            self.open(
                kind="sensory",
                data={
                    "modality": p.modality,
                    "body_region": p.body_region,
                    "intensity": p.intensity,
                    "coherence": p.coherence,
                    "repetition": p.repetition,
                },
            )

    # --------------------------------------------------
    # FRAME OPENING
    # --------------------------------------------------

    def open(self, *, kind: str, data: Dict[str, Any]) -> None:
        """
        Open a new frame.

        Frames are inert containers.
        They do NOT decide meaning or action.
        """

        frame = {
            "kind": kind,
            "data": data,
            "tick_opened": len(self.frames),
        }

        self.frames.append(frame)
        self.active = frame

    # --------------------------------------------------
    # READ-ONLY INTROSPECTION
    # --------------------------------------------------

    def snapshot(self) -> Dict[str, Any]:
        """
        Safe snapshot for UI / debugging.
        """
        return {
            "frame_count": len(self.frames),
            "active_frame": self.active,
        }