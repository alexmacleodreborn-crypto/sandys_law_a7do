from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# TOWN PROFILE (GLOBAL CONTEXT)
# ============================================================

@dataclass(frozen=True)
class TownProfile:
    """
    Global environmental context.

    No agents.
    No memory.
    No time.
    No semantics.

    This defines the *background reality* A7DO is born into.
    """

    name: str
    population: int
    base_temperature: float
    ambient_noise: float
    daylight_level: float

    # --------------------------------------------------------
    # REQUIRED DEFAULT CONSTRUCTOR ✅
    # --------------------------------------------------------

    @classmethod
    def default(cls) -> "TownProfile":
        """
        Minimal valid town.
        Used for birth / Phase 0.
        """
        return cls(
            name="Unnamed Town",
            population=0,
            base_temperature=0.0,
            ambient_noise=0.0,
            daylight_level=0.0,
        )