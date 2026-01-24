# sandys_law_a7do/square/coupling.py

from __future__ import annotations
from dataclasses import dataclass

from sandys_law_a7do.square.state import SquareState


# ============================================================
# Square Coupling Doctrine
#
# Coupling:
# - reads structure
# - never writes back
# - never decides
# - never gates
#
# This is a geometric projection, not a controller.
# ============================================================


@dataclass(frozen=True)
class SquareCouplingInput:
    """
    Structural signals projected into Square.

    All values are normalized [0..1].
    """
    stability: float
    load: float
    coherence: float
    fragmentation: float
    prediction_error: float
    gate_pressure: float
    embodiment_confidence: float


class SquareCoupler:
    """
    Projects system structure into SquareState.

    This class performs NO smoothing and NO inertia.
    That is handled by SquareDynamics.
    """

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def project(self, *, inp: SquareCouplingInput) -> SquareState:
        """
        Convert raw structural inputs into a SquareState.

        This is a direct geometric embedding.
        """

        return SquareState(
            stability=self._clip(inp.stability),
            load=self._clip(inp.load),
            coherence=self._clip(inp.coherence),
            fragmentation=self._clip(inp.fragmentation),
            prediction_error=self._clip(inp.prediction_error),
            gate_pressure=self._clip(inp.gate_pressure),
            embodiment_confidence=self._clip(inp.embodiment_confidence),
        )

    # --------------------------------------------------------
    # Utils
    # --------------------------------------------------------

    @staticmethod
    def _clip(v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return float(v)