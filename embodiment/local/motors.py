# embodiment/local/motors.py

from dataclasses import dataclass
from typing import Literal


MotorType = Literal["flex", "extend", "rotate", "withdraw", "stabilize"]


@dataclass
class MotorImpulse:
    """
    A local motor command.
    Issued by copilot or reflex.
    """
    motor: MotorType
    region: str
    effort: float          # [0..1]
    duration: int          # ticks