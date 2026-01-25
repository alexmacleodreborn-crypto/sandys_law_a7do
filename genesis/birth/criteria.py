# genesis/birth/criteria.py

from __future__ import annotations
from dataclasses import dataclass


# ============================================================
# Birth Criteria Doctrine
#
# Birth is permitted when the system has demonstrated:
# - sustained stability
# - tolerance to rhythmic load
# - no collapse under reflex-only operation
#
# Birth is NOT a reward.
# Birth is a phase transition.
# ============================================================


@dataclass(frozen=True)
class BirthReadiness:
    """
    Structural assessment of birth readiness.
    """
    ready: bool
    reason: str
    stability_score: float
    exposure_time: float


class BirthCriteria:
    """
    Evaluates whether prebirth → birth transition is allowed.
    """

    # --------------------------------------------------------
    # Thresholds (conservative)
    # --------------------------------------------------------
    MIN_EXPOSURE_TIME = 50.0        # time units under womb physics
    MIN_STABILITY = 0.6             # average stability
    MAX_ALLOWED_LOAD = 0.7          # must not exceed repeatedly

    def __init__(self) -> None:
        self._time_exposed = 0.0
        self._stability_integral = 0.0
        self._samples = 0
        self._load_violations = 0

    # --------------------------------------------------------
    # Update with latest signals
    # --------------------------------------------------------

    def update(
        self,
        *,
        dt: float,
        stability: float,
        ambient_load: float,
    ) -> None:
        """
        Feed womb-era structural signals into birth evaluator.
        """
        self._time_exposed += dt
        self._stability_integral += stability
        self._samples += 1

        if ambient_load > self.MAX_ALLOWED_LOAD:
            self._load_violations += 1

    # --------------------------------------------------------
    # Evaluate readiness
    # --------------------------------------------------------

    def evaluate(self) -> BirthReadiness:
        """
        Determine whether birth is permitted.
        """
        if self._samples == 0:
            return BirthReadiness(
                ready=False,
                reason="no_exposure",
                stability_score=0.0,
                exposure_time=0.0,
            )

        avg_stability = self._stability_integral / self._samples

        if self._time_exposed < self.MIN_EXPOSURE_TIME:
            return BirthReadiness(
                ready=False,
                reason="insufficient_exposure_time",
                stability_score=avg_stability,
                exposure_time=self._time_exposed,
            )

        if avg_stability < self.MIN_STABILITY:
            return BirthReadiness(
                ready=False,
                reason="insufficient_stability",
                stability_score=avg_stability,
                exposure_time=self._time_exposed,
            )

        if self._load_violations > self._samples * 0.2:
            return BirthReadiness(
                ready=False,
                reason="excessive_load_instability",
                stability_score=avg_stability,
                exposure_time=self._time_exposed,
            )

        return BirthReadiness(
            ready=True,
            reason="birth_conditions_met",
            stability_score=avg_stability,
            exposure_time=self._time_exposed,
        )