from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from world.world_state import WorldEvent, WorldEventType


# ============================================================
# Phase 1: Prediction Error (No reward, No time)
#
# Prediction error is computed as mismatch between:
#   expected outcome vector  x_hat
#   observed outcome vector  x
#
# This is not belief. This is not value. This is structural mismatch.
# ============================================================


@dataclass(frozen=True)
class Expectation:
    """
    A bounded expectation vector.

    In early phases, expectation is conservative:
    - It can only predict movement outcome likelihood based on recent outcomes
    - It cannot predict hidden world state
    """
    x_hat: Dict[str, float]


@dataclass(frozen=True)
class PredictionErrorResult:
    """
    Prediction error result + interpretation channels for later use.
    """
    error_l1: float
    components: Dict[str, float]
    x_hat: Dict[str, float]
    x_obs: Dict[str, float]


class PredictionErrorEngine:
    """
    Computes prediction error from a short recent event window.

    Input:
      - events: recent events (chronological)
      - expectation: optional expectation vector (if none, returns novelty-based error)
    Output:
      - PredictionErrorResult
    """

    def __init__(self, *, novelty_default: float = 0.25) -> None:
        self.novelty_default = float(novelty_default)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def compute(
        self,
        *,
        recent_events: List[WorldEvent],
        expectation: Optional[Expectation],
    ) -> PredictionErrorResult:
        x_obs = self._extract_observed_vector(recent_events)

        if expectation is None:
            # Early phase: no expectations yet -> treat as novelty
            err = self._clip01(self.novelty_default)
            return PredictionErrorResult(
                error_l1=err,
                components={"novelty": err},
                x_hat={},
                x_obs=x_obs,
            )

        x_hat = dict(expectation.x_hat)
        comps: Dict[str, float] = {}

        # Compare only shared keys; missing keys are treated as zero expectation.
        keys = sorted(set(x_obs.keys()) | set(x_hat.keys()))
        err = 0.0
        for k in keys:
            a = float(x_hat.get(k, 0.0))
            b = float(x_obs.get(k, 0.0))
            d = abs(a - b)
            comps[k] = d
            err += d

        err = self._clip01(err)
        return PredictionErrorResult(
            error_l1=err,
            components=comps,
            x_hat=x_hat,
            x_obs=x_obs,
        )

    def as_event(
        self,
        *,
        parent_id: Optional[str],
        result: PredictionErrorResult,
        source: str = "accounting",
    ) -> WorldEvent:
        """
        Convert prediction error into a WorldEvent-like structure.
        (Still an event stream object; in later phases you may use shared/events instead.)
        """
        return WorldEvent(
            event_id="pe_placeholder",  # caller should replace if using deterministic store
            type=WorldEventType.INTERNAL,
            name="prediction_error",
            payload={
                "error_l1": float(result.error_l1),
                "components": dict(result.components),
                "x_hat": dict(result.x_hat),
                "x_obs": dict(result.x_obs),
                "source": str(source),
            },
            parent_id=parent_id,
        )

    # --------------------------------------------------------
    # Observed vector extraction
    # --------------------------------------------------------

    def _extract_observed_vector(self, events: List[WorldEvent]) -> Dict[str, float]:
        """
        Converts recent OUTCOME events into a minimal observed outcome vector.

        This is intentionally tiny and non-semantic.
        Keys are stable primitives:
          moved_ok: 1 if last outcome was moved else 0
          blocked_ok: 1 if last outcome was blocked else 0
          boundary_block: 1 if reason boundary
          wall_block: 1 if reason wall
        """
        moved = 0.0
        blocked = 0.0
        boundary = 0.0
        wall = 0.0

        for e in reversed(events):
            if e.type != WorldEventType.OUTCOME:
                continue

            if e.name == "moved":
                moved = 1.0
                blocked = 0.0
                boundary = 0.0
                wall = 0.0
                break

            if e.name == "blocked":
                moved = 0.0
                blocked = 1.0
                reason = str(e.payload.get("reason", ""))
                if reason == "blocked_by_boundary":
                    boundary = 1.0
                elif reason == "blocked_by_wall":
                    wall = 1.0
                break

        return {
            "moved": moved,
            "blocked": blocked,
            "blocked_by_boundary": boundary,
            "blocked_by_wall": wall,
        }

    # --------------------------------------------------------
    # Utils
    # --------------------------------------------------------

    @staticmethod
    def _clip01(v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return float(v)
