# genesis/womb/physics.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


# ============================================================
# Womb Physics Doctrine
#
# - External
# - Rhythmic
# - Non-agentic
# - Deterministic
#
# This module represents the physical environment
# before A7DO has agency, memory, or embodiment.
# ============================================================


@dataclass(frozen=True)
class WombSignals:
    """
    External physical signals imposed on the system.
    """

    heartbeat_phase: float        # [0..1] cyclic
    ambient_load: float           # [0..1]
    sensory_intensity: float      # [0..1]
    reflex_allowed: bool          # always True in womb


class WombPhysics:
    """
    Deterministic womb environment.
    """

    # --------------------------------------------------------
    # Parameters (conservative, biological-inspired)
    # --------------------------------------------------------
    HEARTBEAT_RATE = 0.8           # cycles per time unit
    BASE_LOAD = 0.3
    LOAD_VARIANCE = 0.1
    SENSORY_BASE = 0.2
    SENSORY_VARIANCE = 0.15

    def __init__(self) -> None:
        self._time = 0.0

    # --------------------------------------------------------
    # Advance time
    # --------------------------------------------------------

    def step(self, dt: float = 1.0) -> WombSignals:
        """
        Advance womb physics by dt time units.
        """
        self._time += dt

        heartbeat = (self._time * self.HEARTBEAT_RATE) % 1.0

        # Gentle oscillatory load
        load = self.BASE_LOAD + self.LOAD_VARIANCE * self._oscillate(self._time)

        # Soft sensory field
        sensory = self.SENSORY_BASE + self.SENSORY_VARIANCE * self._oscillate(
            self._time + 0.5
        )

        return WombSignals(
            heartbeat_phase=heartbeat,
            ambient_load=self._clip01(load),
            sensory_intensity=self._clip01(sensory),
            reflex_allowed=True,
        )

    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------

    @staticmethod
    def _oscillate(t: float) -> float:
        """
        Simple bounded oscillation in [-1, 1].
        """
        return ((t % 2.0) - 1.0)

    @staticmethod
    def _clip01(v: float) -> float:
        return max(0.0, min(1.0, v))