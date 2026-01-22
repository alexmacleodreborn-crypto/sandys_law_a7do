# embodiment/local/sensors.py

from dataclasses import dataclass
from typing import Literal


SensorType = Literal["touch", "pressure", "thermal", "pain", "position"]


@dataclass
class SensorEvent:
    """
    A raw local bodily signal.
    Sensors do not interpret meaning.
    """
    sensor: SensorType
    region: str
    intensity: float        # normalized [0..1]
    timestamp: int