from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

from world.world_state import WorldEvent, WorldEventType, WorldState
from world.physics import WorldPhysics


# ============================================================
# Phase 0: Actuators
# - Define what actions are physically possible
# - Prevent illegal / undefined actions
# - No learning
# - No reward
# - No time
# ============================================================


@dataclass(frozen=True)
class ActionIntent:
    """
    An action intent is a *request*, not a guarantee.

    It represents the only allowed interface from Mind → World.
    """
    name: str
    payload: Dict[str, float]


class ActuatorSuite:
    """
    Physical actuator interface.

    Doctrine:
    - If an action is not defined here, it cannot exist.
    - Actuators do not decide *whether* an action is good.
    - Actuators only enforce physical validity.
    """

    def __init__(self, state: WorldState) -> None:
        self.state = state
        self.physics = WorldPhysics(state)

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def apply(self, intent: ActionIntent) -> List[WorldEvent]:
        """
        Apply a single action intent.

        Unknown actions are rejected deterministically.
        """
        if intent.name == "move":
            return self._apply_move(intent)

        # ----------------------------------------------------
        # Unknown / illegal action
        # ----------------------------------------------------

        e = self.state.emit(
            type=WorldEventType.SYSTEM,
            name="illegal_action",
            payload={
                "action": intent.name,
                "payload": dict(intent.payload),
            },
        )
        return [e]

    # --------------------------------------------------------
    # Move actuator
    # --------------------------------------------------------

    def _apply_move(self, intent: ActionIntent) -> List[WorldEvent]:
        dx = int(intent.payload.get("dx", 0))
        dy = int(intent.payload.get("dy", 0))

        # Only unit moves are allowed in Phase 0
        if abs(dx) + abs(dy) != 1:
            e = self.state.emit(
                type=WorldEventType.SYSTEM,
                name="illegal_move_vector",
                payload={
                    "dx": dx,
                    "dy": dy,
                },
            )
            return [e]

        return self.physics.apply_move(dx, dy)
