from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class AttentionField:
    """
    Maps structural context → attention bias.

    Preference ∈ [-1, +1]
    Attention ∈ [0.5, 1.5]

    Neutral preference → 1.0
    """
    weights: Dict[str, float]

    def get(self, context_key: str) -> float:
        return float(self.weights.get(context_key, 1.0))