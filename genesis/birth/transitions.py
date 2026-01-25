# genesis/birth/transition.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any

from genesis.birth.criteria import BirthReadiness


# ============================================================
# Birth Transition Doctrine
#
# This module PERFORMS the birth transition.
#
# It does NOT:
# - decide readiness
# - learn
# - write memory
# - write embodiment
#
# It ONLY:
# - flips system mode
# - enables subsystems
# ============================================================


@dataclass(frozen=True)
class BirthTransitionResult:
    transitioned: bool
    reason: str


class BirthTransitionEngine:
    """
    Executes the prebirth → birth transition exactly once.
    """

    def __init__(self) -> None:
        self._completed = False

    def attempt_transition(
        self,
        *,
        readiness: BirthReadiness,
        state: Dict[str, Any],
    ) -> BirthTransitionResult:
        """
        Attempt to transition the system into born state.
        """

        if self._completed:
            return BirthTransitionResult(
                transitioned=False,
                reason="already_born",
            )

        if not readiness.ready:
            return BirthTransitionResult(
                transitioned=False,
                reason=f"not_ready:{readiness.reason}",
            )

        # ----------------------------------------------------
        # APPLY TRANSITION (STRUCTURAL ONLY)
        # ----------------------------------------------------

        # Global phase flag
        state["phase"] = "born"

        # Enable frame lifecycle
        state["frames_enabled"] = True

        # Enable scuttling & reflex coordination
        state["scuttling_enabled"] = True

        # Disable womb physics
        state["womb_active"] = False

        # Birth completed
        self._completed = True

        return BirthTransitionResult(
            transitioned=True,
            reason="birth_transition_completed",
        )