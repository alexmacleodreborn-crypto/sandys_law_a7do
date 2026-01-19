from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Set


# ============================================================
# Preference (Stage C1)
# Structural bias, NOT reward, NOT emotion
# ============================================================

@dataclass
class Preference:
    """
    A single structural preference.
    """
    strength: float = 0.0     # [0..1]
    exposures: int = 0


@dataclass
class PreferenceField:
    """
    Preference Field (Stage C1)

    Preferences grow when prediction error is low
    and decay slowly when not reinforced.

    This field does NOT:
    - choose actions
    - suppress inputs
    - encode identity

    It only biases future integration.
    """

    preferences: Dict[str, Preference] = field(default_factory=dict)

    # Tunables (conservative by design)
    eta: float = 0.05     # learning rate
    decay: float = 0.01   # decay per unseen step

    # --------------------------------------------------------
    # Update rules
    # --------------------------------------------------------

    def update(self, signature: str, prediction_error: float) -> None:
        """
        Reinforce a preference when prediction error is low.
        """
        p = self.preferences.setdefault(signature, Preference())

        gain = self.eta * (1.0 - prediction_error) * (1.0 - p.strength)
        p.strength = max(0.0, min(1.0, p.strength + gain))
        p.exposures += 1

    def decay_unseen(self, seen: Set[str]) -> None:
        """
        Decay preferences that were not reinforced this frame.
        """
        for sig, p in self.preferences.items():
            if sig not in seen:
                p.strength *= (1.0 - self.decay)

    # --------------------------------------------------------
    # Introspection (read-only)
    # --------------------------------------------------------

    def snapshot(self) -> Dict[str, float]:
        """
        Returns preference strengths for dashboards / plots.
        """
        return {k: round(v.strength, 4) for k, v in self.preferences.items()}
