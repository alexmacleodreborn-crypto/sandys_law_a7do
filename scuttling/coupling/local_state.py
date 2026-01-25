from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LocalState:
    """
    Pure local embodied physics.

    No memory.
    No intention.
    No symbols.
    """

    load: float = 0.0
    stability: float = 0.5
    fatigue: float = 0.0
    integrity: float = 1.0

    MAX_LOAD: float = 1.0
    MAX_FATIGUE: float = 1.0
    MIN_INTEGRITY: float = 0.0

    # ---------------------------------
    # Structural updates
    # ---------------------------------

    def apply_load(self, delta: float) -> None:
        self.load = min(self.MAX_LOAD, max(0.0, self.load + delta))
        if delta > 0:
            self.fatigue = min(self.MAX_FATIGUE, self.fatigue + delta * 0.5)
        self._recompute_stability()

    def relieve_load(self, delta: float) -> None:
        self.load = max(0.0, self.load - abs(delta))
        self._recompute_stability()

    def apply_damage(self, severity: float) -> None:
        self.integrity = max(self.MIN_INTEGRITY, self.integrity - abs(severity))
        self._recompute_stability()

    def recover(self, rate: float = 0.02) -> None:
        self.fatigue = max(0.0, self.fatigue - rate)
        self.load = max(0.0, self.load - rate)
        self._recompute_stability()

    # ---------------------------------
    # Internal
    # ---------------------------------

    def _recompute_stability(self) -> None:
        self.stability = max(
            0.0,
            min(
                1.0,
                self.integrity * (1.0 - self.load) * (1.0 - self.fatigue),
            ),
        )

    # ---------------------------------
    # Read-only helpers
    # ---------------------------------

    def overloaded(self) -> bool:
        return self.load >= 0.85

    def unstable(self) -> bool:
        return self.stability <= 0.35

    def exhausted(self) -> bool:
        return self.fatigue >= 0.8