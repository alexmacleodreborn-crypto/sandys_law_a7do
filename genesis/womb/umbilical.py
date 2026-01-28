from __future__ import annotations
from dataclasses import dataclass


@dataclass
class UmbilicalState:
    """
    External life-support link.
    NEVER owned by the agent.
    """
    active: bool
    load_transfer: float
    rhythmic_coupling: float


class UmbilicalLink:
    """
    Models maternal life-support coupling.

    - Supplies energy/load buffering
    - Couples rhythm (heartbeat entrainment)
    - Exists ONLY pre-birth
    """

    BASE_LOAD_TRANSFER = 0.8
    BASE_RHYTHMIC_COUPLING = 0.9

    def __init__(self) -> None:
        self.active = True

    def step(self, *, womb_active: bool) -> UmbilicalState:
        if not womb_active:
            self.active = False

        return UmbilicalState(
            active=self.active,
            load_transfer=self.BASE_LOAD_TRANSFER if self.active else 0.0,
            rhythmic_coupling=self.BASE_RHYTHMIC_COUPLING if self.active else 0.0,
        )