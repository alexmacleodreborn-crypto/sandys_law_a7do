from typing import List
from scuttling.reflex import ReflexTrigger
from world.world_state import WorldState


def extract_reflex_triggers(world: WorldState) -> List[ReflexTrigger]:
    """
    Translate raw physical body state into reflex triggers.
    No cognition, no memory, no meaning.
    """

    triggers: List[ReflexTrigger] = []
    body = world.agent

    # Thermal reflex
    if body.thermal > 0.0:
        triggers.append(
            ReflexTrigger(
                kind="thermal",
                region="skin",
                magnitude=min(1.0, body.thermal),
            )
        )

    # Pressure reflex (contact)
    if body.contact:
        triggers.append(
            ReflexTrigger(
                kind="pressure",
                region="skin",
                magnitude=0.7,
            )
        )

    # Overload reflex
    if body.pain > 0.0:
        triggers.append(
            ReflexTrigger(
                kind="overload",
                region="core",
                magnitude=min(1.0, body.pain),
            )
        )

    return triggers