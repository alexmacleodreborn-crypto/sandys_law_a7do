# sandys_law_a7do/embodiment/boundaries.py

from dataclasses import dataclass
from typing import Literal


BoundaryType = Literal["soft", "hard"]


@dataclass(frozen=True)
class BoundarySignal:
    """
    Emitted when an interaction approaches or crosses a boundary.
    """
    boundary_type: BoundaryType
    severity: float          # [0..1]
    description: str


@dataclass
class BoundaryState:
    """
    Tracks boundary pressure.
    """
    soft_pressure: float = 0.0
    hard_pressure: float = 0.0

    def register(self, signal: BoundarySignal) -> None:
        if signal.boundary_type == "soft":
            self.soft_pressure = min(1.0, self.soft_pressure + signal.severity)
        else:
            self.hard_pressure = min(1.0, self.hard_pressure + signal.severity)

    def reset_soft(self) -> None:
        self.soft_pressure = 0.0
