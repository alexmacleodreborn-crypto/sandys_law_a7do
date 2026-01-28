# world/body_effects.py

from __future__ import annotations
from dataclasses import dataclass

from world.world_state import WorldState, AgentBody


# ============================================================
# BODY EFFECTS — WORLD → BODY ONLY
#
# This module is the ONLY place where the world
# is allowed to influence the body.
#
# - No sensors
# - No cognition
# - No memory
# - No semantics
# ============================================================


@dataclass
class BodyEffectConfig:
    """
    Conservative biological constants.
    """
    thermal_gain: float = 0.4        # how fast skin reacts to environment
    noise_gain: float = 0.3          # how strongly sound vibrates the body
    light_gain: float = 0.2          # how strongly light hits retina
    effort_recovery: float = 0.01    # baseline metabolic recovery


class BodyEffects:
    """
    Applies environmental effects to the physical body.
    """

    def __init__(self, cfg: BodyEffectConfig | None = None) -> None:
        self.cfg = cfg or BodyEffectConfig()

    # --------------------------------------------------------
    # MAIN ENTRY POINT
    # --------------------------------------------------------

    def apply(self, world: WorldState) -> None:
        """
        Mutate the AgentBody based on current world conditions.
        """

        body: AgentBody = world.agent

        # ----------------------------------------------------
        # ENVIRONMENT AT CURRENT LOCATION
        # ----------------------------------------------------
        env = world.world_map.environment_at(body.x, body.y)

        # ----------------------------------------------------
        # THERMAL EFFECT
        # ----------------------------------------------------
        # Skin temperature slowly drifts toward ambient
        body.thermal += (
            env.temperature - body.thermal
        ) * self.cfg.thermal_gain

        # ----------------------------------------------------
        # PAIN FROM OVERLOAD (PURELY PHYSICAL)
        # ----------------------------------------------------
        if body.thermal > world.cfg.pain_threshold:
            body.pain = min(1.0, body.thermal)
        else:
            body.pain *= 0.95  # decay if no longer overloaded

        # ----------------------------------------------------
        # AUDITORY VIBRATION (NO MEANING)
        # ----------------------------------------------------
        # Stored implicitly as body strain (not perception)
        body.effort -= env.noise * self.cfg.noise_gain

        # ----------------------------------------------------
        # LIGHT EXPOSURE (RETINAL ONLY)
        # ----------------------------------------------------
        # No vision yet — this only primes sensors later
        # (we do NOT store it directly here)

        # ----------------------------------------------------
        # METABOLIC RECOVERY
        # ----------------------------------------------------
        body.effort = max(
            0.0,
            min(1.0, body.effort + self.cfg.effort_recovery),
        )