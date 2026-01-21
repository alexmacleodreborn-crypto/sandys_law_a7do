# sandys_law_a7do/accounting/expectation.py
"""
Expectation — Phase 7.1 (STRUCTURAL / NO REWARD)

Purpose:
- Maintain conservative expectations (x_hat) for structural signals
- Context keyed by PreferenceEngine-style context_key
- No action selection, no goals, no reward
- No memory writes (in-memory only)

Expectation is a slow, bounded moving average of observed structure.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Optional, List


# ============================================================
# Data structures
# ============================================================

@dataclass(frozen=True)
class ExpectationVector:
    """
    Bounded expectation vector in [0..1] space where applicable.

    NOTE:
    - fragment_count and unique_actions are stored as normalized [0..1]
      to keep comparisons stable across different episode sizes.
    """
    fragment_density: float      # normalized fragment_count
    action_diversity: float      # normalized unique_actions / max(1, fragment_count)
    coherence: float             # [0..1]
    fragmentation: float         # [0..1]
    block_rate: float            # [0..1]


@dataclass(frozen=True)
class ExpectationUpdate:
    context_key: str
    previous: Optional[ExpectationVector]
    updated: ExpectationVector
    alpha: float
    reason: str


@dataclass
class ExpectationStore:
    """
    In-memory store for expectations.

    Keys are structural context keys (no semantics).
    """
    vectors: Dict[str, ExpectationVector] = field(default_factory=dict)

    def get(self, key: str) -> Optional[ExpectationVector]:
        return self.vectors.get(key)

    def set(self, key: str, vec: ExpectationVector) -> None:
        self.vectors[key] = vec

    def top_keys(self, n: int = 10) -> List[str]:
        # No "value" sorting here (this is not preference). Just stable ordering.
        keys = sorted(self.vectors.keys())
        return keys[: max(0, int(n))]


# ============================================================
# Config
# ============================================================

@dataclass(frozen=True)
class ExpectationConfig:
    """
    Conservative tunables.

    alpha: update rate. Small means slow drift.
    frag_norm: fragment_count normalization divisor (keeps density in [0..1]).
    """
    alpha: float = 0.05
    frag_norm: float = 12.0   # ~12 fragments maps to density 1.0 (clip)
    clip_min: float = 0.0
    clip_max: float = 1.0


# ============================================================
# Engine
# ============================================================

class ExpectationEngine:
    """
    Maintains context-keyed structural expectations.

    IMPORTANT:
    - This engine does not choose actions.
    - It only produces an expectation vector used later by prediction error.
    """

    def __init__(self, store: Optional[ExpectationStore] = None, cfg: Optional[ExpectationConfig] = None) -> None:
        self.store = store or ExpectationStore()
        self.cfg = cfg or ExpectationConfig()

    # --------------------------------------------------------
    # Build observation vector
    # --------------------------------------------------------

    def observed_vector(
        self,
        *,
        fragment_count: int,
        unique_actions: int,
        coherence: float,
        fragmentation: float,
        block_rate: float,
    ) -> ExpectationVector:
        """
        Convert raw structural measures into a bounded observation vector.
        """
        fc = max(0, int(fragment_count))
        ua = max(0, int(unique_actions))

        # fragment_density in [0..1]
        frag_density = self._clip01(fc / float(self.cfg.frag_norm if self.cfg.frag_norm > 0 else 1.0))

        # action_diversity in [0..1]
        # diversity = unique_actions / fragment_count (or 0 if empty)
        if fc <= 0:
            diversity = 0.0
        else:
            diversity = ua / float(fc)
        diversity = self._clip01(diversity)

        return ExpectationVector(
            fragment_density=self._clip01(frag_density),
            action_diversity=self._clip01(diversity),
            coherence=self._clip01(coherence),
            fragmentation=self._clip01(fragmentation),
            block_rate=self._clip01(block_rate),
        )

    # --------------------------------------------------------
    # Update rule (EMA)
    # --------------------------------------------------------

    def update(
        self,
        *,
        context_key: str,
        observed: ExpectationVector,
        reason: str = "episode_close",
    ) -> ExpectationUpdate:
        """
        Update expectation via exponential moving average (EMA).

        expected_new = (1-alpha)*expected_old + alpha*observed

        If no previous expectation exists, we initialize to observed
        (still conservative; later PE can treat first-time as novelty).
        """
        key = str(context_key)
        prev = self.store.get(key)
        a = float(self.cfg.alpha)
        a = max(0.0, min(1.0, a))

        if prev is None:
            updated = observed
            self.store.set(key, updated)
            return ExpectationUpdate(
                context_key=key,
                previous=None,
                updated=updated,
                alpha=a,
                reason=f"{reason}:init",
            )

        updated = ExpectationVector(
            fragment_density=self._ema(prev.fragment_density, observed.fragment_density, a),
            action_diversity=self._ema(prev.action_diversity, observed.action_diversity, a),
            coherence=self._ema(prev.coherence, observed.coherence, a),
            fragmentation=self._ema(prev.fragmentation, observed.fragmentation, a),
            block_rate=self._ema(prev.block_rate, observed.block_rate, a),
        )

        self.store.set(key, updated)

        return ExpectationUpdate(
            context_key=key,
            previous=prev,
            updated=updated,
            alpha=a,
            reason=str(reason),
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _ema(old: float, new: float, a: float) -> float:
        return (1.0 - a) * float(old) + a * float(new)

    @staticmethod
    def _clip01(v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return float(v)