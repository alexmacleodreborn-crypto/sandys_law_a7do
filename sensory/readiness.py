from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


@dataclass
class SensoryChannel:
    enabled: bool
    readiness: float  # 0.0 → 1.0


class SensoryReadiness:
    """
    Sensory gating controller.

    Doctrine:
    - All sensory channels OFF pre-birth
    - Gradual ramp-up post-birth
    - No perception, no learning, no semantics
    """

    def __init__(self) -> None:
        self.channels: Dict[str, SensoryChannel] = {
            "touch": SensoryChannel(False, 0.0),
            "pain": SensoryChannel(False, 0.0),
            "proprioception": SensoryChannel(False, 0.0),
            "temperature": SensoryChannel(False, 0.0),
            "balance": SensoryChannel(False, 0.0),
            "vision": SensoryChannel(False, 0.0),
            "auditory": SensoryChannel(False, 0.0),
        }

    def step(self, *, born: bool) -> None:
        """
        Enable and ramp sensory channels after birth.
        """
        if not born:
            return

        for ch in self.channels.values():
            ch.enabled = True
            ch.readiness = min(1.0, ch.readiness + 0.02)

    def snapshot(self) -> Dict[str, float]:
        """
        Observer-safe snapshot.
        """
        return {
            name: ch.readiness if ch.enabled else 0.0
            for name, ch in self.channels.items()
        }