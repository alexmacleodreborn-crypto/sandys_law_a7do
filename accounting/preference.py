from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Tuple


def clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


@dataclass
class PreferenceEntry:
    value: float = 0.0                 # P(x) in [-1, 1]
    last_error: Optional[float] = None # ε_prev(x)
    visits: int = 0
    last_coherence: float = 0.0
    last_load: float = 0.0


@dataclass(frozen=True)
class PreferenceConfig:
    alpha_C: float = 0.20
    alpha_U: float = 0.25
    alpha_E: float = 0.30
    alpha_L: float = 0.30
    eta: float = 0.08
    decay: float = 0.01  # λ


class PreferenceStore:
    """
    Preference is structural gravity, not reward.
    Updated only at frame close.
    """
    def __init__(self, cfg: PreferenceConfig | None = None) -> None:
        self.cfg = cfg or PreferenceConfig()
        self._prefs: Dict[str, PreferenceEntry] = {}

    def get(self, key: str) -> PreferenceEntry:
        if key not in self._prefs:
            self._prefs[key] = PreferenceEntry()
        return self._prefs[key]

    def update(
        self,
        *,
        key: str,
        coherence: float,          # C_F in [0,1]
        prediction_error: float,   # ε_F
        load: float = 0.0,         # L_F in [0,1]
    ) -> Tuple[float, float, float]:
        e = self.get(key)

        dU = 0.0 if e.last_error is None else max(0.0, float(e.last_error) - float(prediction_error))
        c_term = (2.0 * float(coherence) - 1.0)

        dP = (
            self.cfg.alpha_C * c_term
            + self.cfg.alpha_U * dU
            - self.cfg.alpha_E * float(prediction_error)
            - self.cfg.alpha_L * float(load)
        )

        new_val = (1.0 - self.cfg.decay) * e.value + self.cfg.eta * dP
        e.value = clip(new_val, -1.0, 1.0)

        e.last_error = float(prediction_error)
        e.last_coherence = float(coherence)
        e.last_load = float(load)
        e.visits += 1

        return (e.value, dU, dP)

    def snapshot(self) -> Dict[str, dict]:
        return {
            k: {
                "value": v.value,
                "visits": v.visits,
                "last_error": v.last_error,
                "last_coherence": v.last_coherence,
                "last_load": v.last_load,
            }
            for k, v in self._prefs.items()
        }
