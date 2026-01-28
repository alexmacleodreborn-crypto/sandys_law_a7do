# world/layouts/places/core_places.py

from dataclasses import dataclass
from typing import Tuple, Dict


# ============================================================
# PLACES (Phase 0)
# ------------------------------------------------------------
# A place is:
# - a named region
# - a location in world space
# - an environmental modifier
#
# No memory
# No agents
# No semantics
# ============================================================


@dataclass(frozen=True)
class Place:
    """
    A fixed location in the world.
    """

    name: str
    center: Tuple[int, int]        # (x, y) on the world grid
    radius: int                   # influence radius (Manhattan)

    # Environmental modifiers
    temperature_delta: float      # added to town baseline
    noise_delta: float            # added to town noise


# ------------------------------------------------------------
# CORE PLACES (