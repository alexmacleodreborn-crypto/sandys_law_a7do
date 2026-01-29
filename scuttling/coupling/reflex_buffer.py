from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from scuttling.coupling.reflex_coupling import (
    CoupledReflexOutcome,
)


# ============================================================
# Buffered Reflex State
# ============================================================

@dataclass(frozen=True)
class BufferedReflexState:
    """
    Short-lived integrated reflex state.

    This represents the current reflex posture
    of a local body region or system.
    """
    active: bool
    dominant_action: Optional[str]

    load_delta: float
    stability_delta: float

    age: int                   # ticks since last update
    conflict: bool


# ============================================================
# Reflex Buffer
# ============================================================

class ReflexBuffer:
    """
    Short-term buffer for coupled reflex outcomes.

    Properties:
    - ephemeral
    - decays automatically
    - no memory
    - no gating
    - no cognition
    """

    # Conservative decay parameters
    MAX_AGE = 5                # ticks before buffer fully decays
    LOAD_DECAY = 0.85
    STABILITY_DECAY = 0.9

    def __init__(self) -> None:
        self._state: Optional[BufferedReflexState] = None

    # --------------------------------------------------------
    # Update buffer
    # --------------------------------------------------------

    def update(
        self,
        *,
        outcome: CoupledReflexOutcome,
    ) -> None:
        """
        Incorporate a new coupled reflex outcome.
        """
        if not outcome.triggered:
            return

        self._state = BufferedReflexState(
            active=True,
            dominant_action=(
                outcome.dominant_action.name
                if outcome.dominant_action
                else None
            ),
            load_delta=outcome.net_load_delta,
            stability_delta=outcome.net_stability_delta,
            age=0,
            conflict=outcome.unresolved_conflict,
        )

    # --------------------------------------------------------
    # Tick / decay
    # --------------------------------------------------------

    def tick(self) -> None:
        """
        Advance buffer by one tick.
        Applies decay and expires old states.
        """
        if self._state is None:
            return

        age = self._state.age + 1

        if age >= self.MAX_AGE:
            self._state = None
            return

        self._state = BufferedReflexState(
            active=True,
            dominant_action=self._state.dominant_action,
            load_delta=self._state.load_delta * self.LOAD_DECAY,
            stability_delta=self._state.stability_delta * self.STABILITY_DECAY,
            age=age,
            conflict=self._state.conflict,
        )

    # --------------------------------------------------------
    # Read-only access
    # --------------------------------------------------------

    def current(self) -> Optional[BufferedReflexState]:
        """
        Return the current buffered reflex state.
        """
        return self._state