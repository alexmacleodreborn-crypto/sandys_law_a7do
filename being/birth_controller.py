from __future__ import annotations

from sandys_law_a7do.being.birth_state import BirthState


class BirthController:
    """
    Determines when A7DO transitions from pre-birth to born.

    This controller:
    - is deterministic
    - runs automatically
    - has no side effects except state flagging
    """

    def __init__(self) -> None:
        self._born = False
        self._birth_tick: int | None = None

    # --------------------------------------------------
    # Public API
    # --------------------------------------------------

    def evaluate(self, *, state: dict) -> BirthState:
        """
        Evaluate whether birth should occur.

        Called automatically by system startup or early ticks.
        """

        if self._born:
            return BirthState(
                prebirth=False,
                born=True,
                tick_of_birth=self._birth_tick,
                reason="already_born",
            )

        if not self._birth_conditions_met(state):
            return BirthState(
                prebirth=True,
                born=False,
                tick_of_birth=None,
                reason="conditions_not_met",
            )

        # 🔑 Birth event
        self._born = True
        self._birth_tick = int(state.get("ticks", 0))

        return BirthState(
            prebirth=False,
            born=True,
            tick_of_birth=self._birth_tick,
            reason="structural_viability",
        )

    # --------------------------------------------------
    # Conditions
    # --------------------------------------------------

    def _birth_conditions_met(self, state: dict) -> bool:
        """
        Conservative viability checks.
        """

        # Must have scuttling substrate
        if "frames" not in state:
            return False

        # Must have reflex capability
        if "reflex_engine" not in state and "reflex" not in state:
            return False

        # Must have local load tracking
        load = float(state.get("structural_load", 1.0))
        if load > 0.9:
            return False

        # Must have body map (ownership substrate)
        body_map = state.get("body_map")
        if body_map is None:
            return False
        if not getattr(body_map, "regions", None):
            return False

        return True