from __future__ import annotations
from dataclasses import dataclass


@dataclass
class LocalState:
    load: float = 0.0
    stability: float = 0.6
    fatigue: float = 0.0
    integrity: float = 1.0

    def recover(self, rate: float = 0.01) -> None:
        self.fatigue = max(0.0, self.fatigue - rate)
        self.load = max(0.0, self.load - rate)
        self._recompute()

    def _recompute(self) -> None:
        self.stability = max(
            0.0,
            min(
                1.0,
                self.integrity * (1.0 - self.load) * (1.0 - self.fatigue),
            ),
        )