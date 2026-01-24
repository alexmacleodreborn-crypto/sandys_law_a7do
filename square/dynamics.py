# sandys_law_a7do/square/dynamics.py

from __future__ import annotations
from dataclasses import dataclass

from sandys_law_a7do.square.state import SquareState


# ============================================================
# Square Dynamics Doctrine
#
# Square dynamics are:
# - slow
# - inertial
# - monotonic where possible
# - resistant to noise
#
# Square does NOT react instantly.
# It integrates pressure over time.
# ============================================================


@dataclass(frozen=True)
class SquareDynamicsConfig:
    """
    Tunable rates for square evolution.

    These should remain SMALL.
    """
    alpha: float = 0.05     # base update rate
    decay: float = 0.02     # relaxation toward neutral
    clip_min: float = 0.0
    clip_max: float = 1.0


class SquareDynamics:
    """
    Evolves SquareState from structural inputs.

    This class:
    - does not read sensors
    - does not see actions
    - does not know semantics
    """

    def __init__(self, cfg: SquareDynamicsConfig | None = None) -> None:
        self.cfg = cfg or SquareDynamicsConfig()

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def step(
        self,
        *,
        prev: SquareState,
        stability: float,
        load: float,
        coherence: float,
        fragmentation: float,
        prediction_error: float,
        gate_pressure: float,
        embodiment_confidence: float,
    ) -> SquareState:
        """
        Produce the next SquareState.

        All inputs are expected in [0..1].
        """

        a = self.cfg.alpha
        d = self.cfg.decay

        def upd(old: float, new: float) -> float:
            # slow drift toward signal, slight decay toward neutral
            v = old + a * (new - old)
            v *= (1.0 - d)
            return self._clip(v)

        return SquareState(
            stability=upd(prev.stability, stability),
            load=upd(prev.load, load),
            coherence=upd(prev.coherence, coherence),
            fragmentation=upd(prev.fragmentation, fragmentation),
            prediction_error=upd(prev.prediction_error, prediction_error),
            gate_pressure=upd(prev.gate_pressure, gate_pressure),
            embodiment_confidence=upd(
                prev.embodiment_confidence,
                embodiment_confidence,
            ),
        )

    # --------------------------------------------------------
    # Utils
    # --------------------------------------------------------

    def _clip(self, v: float) -> float:
        if v < self.cfg.clip_min:
            return self.cfg.clip_min
        if v > self.cfg.clip_max:
            return self.cfg.clip_max
        return float(v)