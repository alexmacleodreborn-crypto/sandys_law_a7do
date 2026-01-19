from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict

def l1(a: Dict[str, float], b: Dict[str, float]) -> float:
    keys = set(a.keys()) | set(b.keys())
    return sum(abs(a.get(k, 0.0) - b.get(k, 0.0)) for k in keys)

@dataclass
class ExpectationModel:
    """
    Identity-owned expectation over fragment kinds.
    """
    beta: float = 0.10
    q: Dict[str, float] = field(default_factory=dict)

    def predict(self) -> Dict[str, float]:
        return dict(self.q)

    def update(self, p_obs: Dict[str, float]) -> None:
        # q <- (1-beta)q + beta p
        keys = set(self.q.keys()) | set(p_obs.keys())
        q_new: Dict[str, float] = {}
        for k in keys:
            q_new[k] = (1.0 - self.beta) * self.q.get(k, 0.0) + self.beta * p_obs.get(k, 0.0)

        # normalize
        s = sum(q_new.values())
        if s > 0:
            for k in list(q_new.keys()):
                q_new[k] = q_new[k] / s

        self.q = q_new
