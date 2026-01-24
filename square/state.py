# sandys_law_a7do/square/state.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


# ============================================================
# Square Doctrine (Macroscopic Layer)
#
# Square represents the GLOBAL structural condition of A7DO.
#
# Square is:
# - slow
# - inertial
# - macroscopic
# - non-decision-making
#
# Square is NOT:
# - a controller
# - a planner
# - a gate
# - a memory writer
#
# Square only *describes* the system.
# ============================================================


@dataclass(frozen=True)
class SquareState:
    """
    A macroscopic snapshot of the system's structural condition.

    All values are normalized to [0..1].

    SquareState MUST be:
    - conservative
    - interpretable
    - derived from existing signals
    """

    # --------------------------------------------------------
    # Core structural axes
    # --------------------------------------------------------

    stability: float
    """
    Global structural stability.
    High when resolution is sustained.
    Low when instability persists.
    """

    load: float
    """
    Global structural load.
    High when pressure accumulates.
    Low when system is relaxed.
    """

    coherence: float
    """
    Global coherence.
    Measures alignment between action and outcome.
    """

    fragmentation: float
    """
    Global fragmentation.
    Measures entropy / dispersion of events.
    """

    # --------------------------------------------------------
    # Predictive stress
    # --------------------------------------------------------

    prediction_error: float
    """
    Global prediction error pressure.
    High when outcomes diverge from expectations.
    """

    # --------------------------------------------------------
    # Gate pressure (aggregate)
    # --------------------------------------------------------

    gate_pressure: float
    """
    Aggregate resistance from gates.
    High when many gates are closing or constrained.
    """

    # --------------------------------------------------------
    # Embodiment confidence
    # --------------------------------------------------------

    embodiment_confidence: float
    """
    Confidence derived from embodied invariants.
    Rises slowly; decays conservatively.
    """

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    def as_dict(self) -> Dict[str, float]:
        """
        Export square state as a simple dictionary.
        """
        return {
            "stability": self.stability,
            "load": self.load,
            "coherence": self.coherence,
            "fragmentation": self.fragmentation,
            "prediction_error": self.prediction_error,
            "gate_pressure": self.gate_pressure,
            "embodiment_confidence": self.embodiment_confidence,
        }