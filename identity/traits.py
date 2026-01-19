from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional


def clip(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


@dataclass
class TraitConfig:
    # Minimum evidence
    min_observations: int = 5

    # Thresholds
    min_strength: float = 0.65
    min_coherence: float = 0.55
    max_prediction_error: float = 0.85

    # EMA smoothing for candidate stats (event-count based)
    ema_beta: float = 0.35


@dataclass
class TraitCandidate:
    signature: str
    observations: int = 0

    # EMA stats
    strength_ema: float = 0.0
    coherence_ema: float = 0.0
    pred_err_ema: float = 1.0

    def update(self, *, strength: float, coherence: float, prediction_error: float, beta: float) -> None:
        self.observations += 1
        b = float(beta)

        self.strength_ema = (1.0 - b) * self.strength_ema + b * float(strength)
        self.coherence_ema = (1.0 - b) * self.coherence_ema + b * float(coherence)
        self.pred_err_ema = (1.0 - b) * self.pred_err_ema + b * float(prediction_error)


@dataclass
class TraitRecord:
    """
    A structural trait = a crystallized invariant.
    Not a semantic label.
    """
    trait_id: str
    signature: str
    confidence: float
    observations: int

    strength_ema: float
    coherence_ema: float
    pred_err_ema: float

    def to_dict(self) -> Dict[str, float | int | str]:
        return {
            "trait_id": self.trait_id,
            "signature": self.signature,
            "confidence": self.confidence,
            "observations": self.observations,
            "strength_ema": self.strength_ema,
            "coherence_ema": self.coherence_ema,
            "pred_err_ema": self.pred_err_ema,
        }


class TraitCrystallizer:
    """
    Stage B:
    Convert repeated stable traces into identity traits.
    """

    def __init__(self, cfg: Optional[TraitConfig] = None) -> None:
        self.cfg = cfg or TraitConfig()
        self._candidates: Dict[str, TraitCandidate] = {}

    def update(
        self,
        *,
        signature: str,
        trace_strength: float,
        coherence: float,
        prediction_error: float,
    ) -> Optional[TraitRecord]:
        sig = str(signature).strip()
        if not sig:
            return None

        cand = self._candidates.get(sig)
        if cand is None:
            cand = TraitCandidate(signature=sig)
            self._candidates[sig] = cand

        cand.update(
            strength=float(trace_strength),
            coherence=float(coherence),
            prediction_error=float(prediction_error),
            beta=self.cfg.ema_beta,
        )

        # Crystallization gate
        if cand.observations < self.cfg.min_observations:
            return None
        if cand.strength_ema < self.cfg.min_strength:
            return None
        if cand.coherence_ema < self.cfg.min_coherence:
            return None
        if cand.pred_err_ema > self.cfg.max_prediction_error:
            return None

        # Trait confidence (bounded)
        conf = clip(
            0.25 * cand.strength_ema
            + 0.25 * cand.coherence_ema
            + 0.50 * (1.0 - cand.pred_err_ema),
            0.0,
            1.0,
        )

        trait_id = f"invariant::{sig}"
        return TraitRecord(
            trait_id=trait_id,
            signature=sig,
            confidence=conf,
            observations=cand.observations,
            strength_ema=cand.strength_ema,
            coherence_ema=cand.coherence_ema,
            pred_err_ema=cand.pred_err_ema,
        )

    def snapshot_candidates(self) -> Dict[str, dict]:
        return {
            k: {
                "observations": v.observations,
                "strength_ema": v.strength_ema,
                "coherence_ema": v.coherence_ema,
                "pred_err_ema": v.pred_err_ema,
            }
            for k, v in self._candidates.items()
        }
