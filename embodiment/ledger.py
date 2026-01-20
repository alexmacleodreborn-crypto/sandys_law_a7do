# sandys_law_a7do/embodiment/ledger.py

from typing import List, Union
from .boundaries import BoundarySignal
from .thermal_pain import ThermalPainSignal


EmbodimentEvent = Union[BoundarySignal, ThermalPainSignal]


class EmbodimentLedger:
    """
    Lightweight recorder of embodiment-related signals.
    """
    def __init__(self):
        self.events: List[EmbodimentEvent] = []

    def record(self, event: EmbodimentEvent) -> None:
        self.events.append(event)

    def recent(self, n: int = 10) -> List[EmbodimentEvent]:
        return self.events[-n:]
