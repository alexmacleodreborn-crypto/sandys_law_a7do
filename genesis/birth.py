# genesis/birth.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


# ============================================================
# Birth Doctrine
#
# Birth is a PHASE TRANSITION.
#
# Birth:
# - does NOT create intelligence
# - does NOT create choice
# - does NOT create goals
# - does NOT create memory meaning
#
# Birth ONLY:
# - transfers control from environment → internal gates
# - enables consolidation eligibility
# - enables observer interfaces
#
# Birth happens ONCE.
# ============================================================


# ------------------------------------------------------------
# Birth State
# ------------------------------------------------------------

@dataclass(frozen=True)
class BirthState:
    """
    Immutable snapshot of birth status.
    """
    born: bool
    reason: str
    tick: int


# ------------------------------------------------------------
# Birth Evaluator
# ------------------------------------------------------------

class BirthEvaluator:
    """
    Deterministic evaluator for the birth transition.

    Inputs are structural metrics ONLY.
    """

    # --------------------------------------------------------
    # Conservative thresholds (Phase 1)
    # --------------------------------------------------------
    MIN_TICKS = 50                 # minimum time in prebirth
    MIN_STABILITY = 0.6
    MAX_LOAD = 0.4
    MAX_FRAGMENTATION = 0.6

    REQUIRED_FRAMES_STABLE = 5     # consecutive stable frames

    def __init__(self) -> None:
        self._stable_frames = 0
        self._born = False
        self._birth_tick: int | None = None

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def evaluate(
        self,
        *,
        tick: int,
        metrics: Dict[str, float],
    ) -> BirthState:
        """
        Evaluate whether birth should occur.

        This function MUST:
        - be deterministic
        - be monotonic (born never reverts)
        - have no side effects
        """

        if self._born:
            return BirthState(
                born=True,
                reason="already_born",
                tick=self._birth_tick or tick,
            )

        # ----------------------------------------------------
        # Extract metrics safely
        # ----------------------------------------------------
        stability = float(metrics.get("Stability", 0.0))
        load = float(metrics.get("Load", 1.0))
        fragmentation = float(metrics.get("Z", 1.0))

        # ----------------------------------------------------
        # Hard minimum time gate
        # ----------------------------------------------------
        if tick < self.MIN_TICKS:
            return BirthState(
                born=False,
                reason="insufficient_time",
                tick=tick,
            )

        # ----------------------------------------------------
        # Stability window tracking
        # ----------------------------------------------------
        if (
            stability >= self.MIN_STABILITY
            and load <= self.MAX_LOAD
            and fragmentation <= self.MAX_FRAGMENTATION
        ):
            self._stable_frames += 1
        else:
            self._stable_frames = 0

        # ----------------------------------------------------
        # Birth condition
        # ----------------------------------------------------
        if self._stable_frames >= self.REQUIRED_FRAMES_STABLE:
            self._born = True
            self._birth_tick = tick

            return BirthState(
                born=True,
                reason="structural_stability_reached",
                tick=tick,
            )

        return BirthState(
            born=False,
            reason="stability_not_yet_sustained",
            tick=tick,
        )