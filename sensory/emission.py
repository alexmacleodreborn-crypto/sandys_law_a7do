# sensory/emission.py

from __future__ import annotations
from typing import Dict

from world.world_state import WorldState
from genesis.birth_state import BirthState


def emit_raw_sensory(
    *,
    world: WorldState,
    birth: BirthState | None,
) -> Dict[str, float]:
    """
    Convert BODY + WORLD PHYSICS into RAW sensory flux.

    Doctrine:
    - No semantics
    - No perception
    - No memory
    - No symbols
    - Pure involuntary leakage
    """

    agent = world.agent

    # -------------------------------------------------
    # If not born → womb silence
    # -------------------------------------------------
    if birth is None or not birth.born:
        return {
            "vision": 0.0,
            "sound": 0.0,
            "touch": 0.0,
            "temperature": 0.0,
            "pain": 0.0,
            "proprioception": 0.0,
        }

    # -------------------------------------------------
    # POST-BIRTH RAW FLUX
    # -------------------------------------------------

    # Vision = ambient light noise (no shapes)
    vision = 0.05

    # Sound = environmental vibration (constant hum)
    sound = 0.08

    # Touch = contact pressure only
    touch = 0.2 if agent.contact else 0.02

    # Temperature = only when touching something
    temperature = agent.thermal if agent.contact else 0.0

    # Pain = overload only
    pain = agent.pain

    # Proprioception = effort drain (body fatigue)
    proprioception = max(0.0, 1.0 - agent.effort)

    return {
        "vision": round(vision, 3),
        "sound": round(sound, 3),
        "touch": round(touch, 3),
        "temperature": round(temperature, 3),
        "pain": round(pain, 3),
        "proprioception": round(proprioception, 3),
    }