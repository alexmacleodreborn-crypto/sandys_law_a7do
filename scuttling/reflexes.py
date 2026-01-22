from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict, Any


# ============================================================
# Reflex Doctrine
#
# A reflex is:
# - local
# - fast
# - non-symbolic
# - non-gated
# - non-remembered
#
# Reflexes do NOT:
# - plan
# - reason
# - choose
# - write memory
#
# Reflexes MAY:
# - reduce load
# - protect integrity
# - trigger immediate motion
# ============================================================


# ------------------------------------------------------------
# Reflex Trigger
# ------------------------------------------------------------

@dataclass(frozen=True)
class ReflexTrigger:
    """
    Structural condition that can activate a reflex.
    """
    kind: str                     # e.g. "thermal", "pressure", "overload"
    region: str                   # body region
    magnitude: float              # normalized [0..1]
    source: str = "local"          # always local in Phase 1


# ------------------------------------------------------------
# Reflex Action
# ------------------------------------------------------------

@dataclass(frozen=True)
class ReflexAction:
    """
    Immediate motor consequence of a reflex.
    """
    name: str                     # e.g. "withdraw", "release", "stiffen"
    target_region: str
    intensity: float              # [0..1]
    reason: str


# ------------------------------------------------------------
# Reflex Result
# ------------------------------------------------------------

@dataclass(frozen=True)
class ReflexResult:
    """
    Output of reflex evaluation.
    """
    triggered: bool
    action: Optional[ReflexAction]
    load_delta: float             # negative reduces load
    stability_delta: float        # usually positive


# ------------------------------------------------------------
# Core Reflex Engine
# ------------------------------------------------------------

class ReflexEngine:
    """
    Evaluates raw local signals and produces immediate reflex actions.
    """

    # ----------------------------
    # Thresholds (conservative)
    # ----------------------------
    THERMAL_THRESHOLD = 0.65
    PRESSURE_THRESHOLD = 0.7
    OVERLOAD_THRESHOLD = 0.8

    # ----------------------------
    # Main evaluation
    # ----------------------------
    def evaluate(
        self,
        *,
        trigger: ReflexTrigger,
        current_load: float,
        current_stability: float,
    ) -> ReflexResult:
        """
        Evaluate a single reflex trigger.

        This function MUST be:
        - deterministic
        - fast
        - side-effect free
        """

        if trigger.kind == "thermal":
            return self._thermal_reflex(trigger, current_load, current_stability)

        if trigger.kind == "pressure":
            return self._pressure_reflex(trigger, current_load, current_stability)

        if trigger.kind == "overload":
            return self._overload_reflex(trigger, current_load, current_stability)

        # Unknown triggers do nothing
        return ReflexResult(
            triggered=False,
            action=None,
            load_delta=0.0,
            stability_delta=0.0,
        )

    # --------------------------------------------------------
    # Specific reflexes
    # --------------------------------------------------------

    def _thermal_reflex(
        self,
        trigger: ReflexTrigger,
        load: float,
        stability: float,
    ) -> ReflexResult:
        if trigger.magnitude < self.THERMAL_THRESHOLD:
            return self._no_reflex()

        return ReflexResult(
            triggered=True,
            action=ReflexAction(
                name="withdraw",
                target_region=trigger.region,
                intensity=min(1.0, trigger.magnitude),
                reason="thermal_protection",
            ),
            load_delta=-0.2,
            stability_delta=+0.1,
        )

    def _pressure_reflex(
        self,
        trigger: ReflexTrigger,
        load: float,
        stability: float,
    ) -> ReflexResult:
        if trigger.magnitude < self.PRESSURE_THRESHOLD:
            return self._no_reflex()

        return ReflexResult(
            triggered=True,
            action=ReflexAction(
                name="release",
                target_region=trigger.region,
                intensity=min(1.0, trigger.magnitude),
                reason="pressure_relief",
            ),
            load_delta=-0.15,
            stability_delta=+0.05,
        )

    def _overload_reflex(
        self,
        trigger: ReflexTrigger,
        load: float,
        stability: float,
    ) -> ReflexResult:
        if trigger.magnitude < self.OVERLOAD_THRESHOLD:
            return self._no_reflex()

        return ReflexResult(
            triggered=True,
            action=ReflexAction(
                name="halt",
                target_region=trigger.region,
                intensity=1.0,
                reason="system_overload",
            ),
            load_delta=-0.3,
            stability_delta=+0.15,
        )

    # --------------------------------------------------------
    # Utility
    # --------------------------------------------------------

    @staticmethod
    def _no_reflex() -> ReflexResult:
        return ReflexResult(
            triggered=False,
            action=None,
            load_delta=0.0,
            stability_delta=0.0,
        )