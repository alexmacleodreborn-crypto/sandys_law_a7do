# genesis/womb/physics.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


# ============================================================
# Womb Physics Doctrine
#
# - External environment
# - Deterministic
# - Rhythmic
# - Non-interactive
#
# Womb physics:
# - does NOT learn
# - does NOT gate
# - does NOT allow choice
# - does NOT write memory
#
# It only exposes structure over time.
# ============================================================


@dataclass
class WombState:
    """
    Current physical womb conditions.
    """
    tick: int
    heartbeat_rate: float       # beats per tick
    ambient_load: float         # [0..1]
    rhythmic_stability: float   # [0..1]
    womb_active: bool = True


class WombPhysicsEngine:
    """
    Generates deterministic womb signals over time.
    """

    # ---------------------------------
    # Constants (conservative, stable)
    # ---------------------------------
    BASE_HEARTBEAT = 0.25        # baseline rhythmic pulse
    HEARTBEAT_VARIANCE = 0.02
    BASE_LOAD = 0.15
    LOAD_DRIFT = 0.001

    def __init__(self) -> None:
        self._tick = 0

    # ---------------------------------
    # Step
    # ---------------------------------

    def step(self) -> WombState:
        """
        Advance womb physics by one tick.
        """

        self._tick += 1

        # Rhythmic heartbeat (slow oscillation)
        heartbeat = (
            self.BASE_HEARTBEAT
            + self.HEARTBEAT_VARIANCE
            * ((self._tick % 20) - 10) / 10.0
        )

        # Ambient load rises very slowly over time
        load = min(
            0.35,
            self.BASE_LOAD + self._tick * self.LOAD_DRIFT,
        )

        # Stability increases as rhythm becomes predictable
        rhythmic_stability = min(1.0, 0.3 + self._tick * 0.002)

        return WombState(
            tick=self._tick,
            heartbeat_rate=round(heartbeat, 4),
            ambient_load=round(load, 4),
            rhythmic_stability=round(rhythmic_stability, 4),
            womb_active=True,
        )

    # ---------------------------------
    # Snapshot helper (dashboard safe)
    # ---------------------------------

    @staticmethod
    def as_dict(state: WombState) -> Dict[str, float]:
        return {
            "tick": state.tick,
            "heartbeat_rate": state.heartbeat_rate,
            "ambient_load": state.ambient_load,
            "rhythmic_stability": state.rhythmic_stability,
            "womb_active": state.womb_active,
        }