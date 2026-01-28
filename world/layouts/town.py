# world/layouts/town.py

from dataclasses import dataclass


# ============================================================
# WORLD IDENTITY (Phase 0)
# ------------------------------------------------------------
# This file defines WHAT the world is,
# not how it behaves.
#
# - No agents
# - No physics
# - No semantics
# - No cognition
#
# Just environmental truth.
# ============================================================


@dataclass(frozen=True)
class TownProfile:
    """
    Immutable identity of the world.
    """

    name: str
    season: str

    # Environmental baselines
    ambient_temperature: float      # baseline temperature
    ambient_noise: float            # baseline sound floor (0..1)

    # Population (for future noise / motion only)
    population: int


# ------------------------------------------------------------
# DEFAULT TOWN (A7DO BIRTH WORLD)
# ------------------------------------------------------------

DEFAULT_TOWN = TownProfile(
    name="Hearth",
    season="early_spring",

    # Gentle, stable environment
    ambient_temperature=0.15,   # slightly warm
    ambient_noise=0.05,         # near silence

    population=1240,
)