# sensory/wall.py

from dataclasses import dataclass
from typing import Dict, List


@dataclass
class SensoryPacket:
    """
    Pre-semantic sensory unit.
    """
    modality: str          # vision, sound, touch, smell
    body_region: str       # eye, ear, skin, mouth
    intensity: float       # 0..1
    coherence: float       # how structured it is
    repetition: float      # how often recently seen


class SensoryWall:
    """
    Developmental sensory filter.

    Converts raw signals → pre-semantic packets.
    """

    def __init__(self) -> None:
        self.history: Dict[str, float] = {}

    def filter(
        self,
        *,
        raw_input: Dict[str, float],
        anatomy: Dict[str, dict],
        sensory_readiness: Dict[str, float],
    ) -> List[SensoryPacket]:
        packets: List[SensoryPacket] = []

        for channel, intensity in raw_input.items():
            readiness = sensory_readiness.get(channel, 0.0)
            if readiness <= 0.0:
                continue

            body_region = self._map_channel_to_body(channel)
            if body_region not in anatomy:
                continue

            growth = anatomy[body_region]["growth"]
            if growth < 0.3:
                continue  # organ not mature

            key = f"{channel}:{body_region}"
            prev = self.history.get(key, 0.0)
            repetition = min(1.0, prev + 0.1)

            coherence = min(
                1.0,
                readiness * growth * repetition
            )

            packets.append(
                SensoryPacket(
                    modality=channel,
                    body_region=body_region,
                    intensity=intensity,
                    coherence=coherence,
                    repetition=repetition,
                )
            )

            self.history[key] = repetition

        return packets

    @staticmethod
    def _map_channel_to_body(channel: str) -> str:
        return {
            "vision": "eye",
            "sound": "ear",
            "touch": "skin",
            "smell": "nose",
            "taste": "mouth",
        }.get(channel, "")