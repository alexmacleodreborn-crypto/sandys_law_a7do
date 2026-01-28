from typing import Dict
from embodiment.sensory.schema import SensoryChannel


class SensoryReadiness:
    """
    Declares which sensory channels are structurally allowed
    per body region.

    This class:
    - does NOT read the world
    - does NOT generate signals
    - does NOT learn
    """

    def __init__(self):
        # region -> channel -> readiness [0..1]
        self._map: Dict[str, Dict[SensoryChannel, float]] = {}

    def set_region(
        self,
        region: str,
        *,
        touch: float = 0.0,
        pain: float = 0.0,
        proprioception: float = 0.0,
        temperature: float = 0.0,
        balance: float = 0.0,
    ) -> None:
        self._map[region] = {
            SensoryChannel.TOUCH: touch,
            SensoryChannel.PAIN: pain,
            SensoryChannel.PROPRIOCEPTION: proprioception,
            SensoryChannel.TEMPERATURE: temperature,
            SensoryChannel.BALANCE: balance,
        }

    def snapshot(self) -> Dict[str, Dict[str, float]]:
        return {
            region: {ch.value: v for ch, v in channels.items()}
            for region, channels in self._map.items()
        }