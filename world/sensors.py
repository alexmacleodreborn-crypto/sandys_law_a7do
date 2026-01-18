from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from world.world_state import WorldEvent, WorldEventType, WorldState


# ============================================================
# Phase 0: Sensors
# - Convert physical body state → percepts
# - HARD information gating
# - No memory
# - No semantics
# - No time
# ============================================================


@dataclass(frozen=True)
class Percept:
    """
    A percept is *allowed information* emitted by the world.

    IMPORTANT:
    - Sensors do NOT expose full world state
    - Sensors do NOT infer meaning
    - Sensors do NOT store memory
    """
    name: str
    payload: Dict[str, float]


class SensorSuite:
    """
    The only gateway from World → Mind.

    Doctrine:
    - If information is not physically available, it is not emitted.
    - Sensors are local, gated, and conservative.
    """

    def __init__(self, state: WorldState) -> None:
        self.state = state

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def sense(self) -> List[WorldEvent]:
        """
        Generate observation events from the current physical state.

        These are WORLD observation events, not cognition.
        """
        events: List[WorldEvent] = []
        agent = self.state.agent

        # ----------------------------------------------------
        # Contact sensor
        # ----------------------------------------------------

        if agent.contact:
            e = self.state.emit(
                type=WorldEventType.OBSERVATION,
                name="contact",
                payload={
                    "count": float(len(agent.contact_normals)),
                },
            )
            events.append(e)

        # ----------------------------------------------------
        # Directional wall contact (normals)
        # ----------------------------------------------------

        for nx, ny in agent.contact_normals:
            e = self.state.emit(
                type=WorldEventType.OBSERVATION,
                name="contact_direction",
                payload={
                    "nx": float(nx),
                    "ny": float(ny),
                },
            )
            events.append(e)

        # ----------------------------------------------------
        # Thermal sensor (STRICTLY gated)
        # ----------------------------------------------------

        if agent.contact:
            e = self.state.emit(
                type=WorldEventType.OBSERVATION,
                name="thermal",
                payload={
                    "value": float(agent.thermal),
                },
            )
            events.append(e)

        # ----------------------------------------------------
        # Pain sensor (physical overload only)
        # ----------------------------------------------------

        if agent.pain > 0.0:
            e = self.state.emit(
                type=WorldEventType.OBSERVATION,
                name="pain",
                payload={
                    "value": float(agent.pain),
                },
            )
            events.append(e)

        # ----------------------------------------------------
        # Effort sensor (proprioception)
        # ----------------------------------------------------

        e = self.state.emit(
            type=WorldEventType.OBSERVATION,
            name="effort",
            payload={
                "value": float(agent.effort),
            },
        )
        events.append(e)

        return events
