from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# Preference Doctrine (No Reward)
#
# Preference is NOT a reward signal.
# Preference is a slow, bounded bias toward stability.
#
# Inputs:
#   - coherence (settling)
#   - fragmentation (instability)
#   - prediction_error (mismatch / novelty)
#   - load proxies (blocking, overload notes)
#
# Outputs:
#   - preference scores for "contexts"
#
# Contexts are keyed by small, structural signatures (not semantics).
# ============================================================


@dataclass(frozen=True)
class PreferenceUpdate:
    context_key: str
    previous: float
    updated: float
    delta: float
    reason: str


@dataclass
class PreferenceStore:
    """
    Stores preferences in-memory (Phase 1).
    Persistence can be added later through Memory/Ledger layers.

    Values are in [-1, +1].
    """
    prefs: Dict[str, float] = field(default_factory=dict)

    def get(self, key: str) -> float:
        return float(self.prefs.get(key, 0.0))

    def set(self, key: str, value: float) -> None:
        self.prefs[key] = float(value)

    def top(self, n: int = 10) -> List[tuple[str, float]]:
        return sorted(self.prefs.items(), key=lambda kv: kv[1], reverse=True)[: max(0, int(n))]


@dataclass(frozen=True)
class PreferenceConfig:
    """
    Tunables. Keep small and conservative.
    """
    lr: float = 0.08               # learning rate (slow drift)
    decay: float = 0.01            # drift back toward neutral over updates
    clip_min: float = -1.0
    clip_max: float = 1.0

    # Weighting of stability terms (all bounded inputs in [0..1])
    w_coherence: float = 0.55
    w_frag: float = 0.35
    w_error: float = 0.35
    w_blocking: float = 0.20


class PreferenceEngine:
    """
    Computes and updates preferences from structural accounting only.

    It does NOT select actions.
    It produces a bias scalar used later by attention/exploration.
    """

    def __init__(self, store: Optional[PreferenceStore] = None, cfg: Optional[PreferenceConfig] = None) -> None:
        self.store = store or PreferenceStore()
        self.cfg = cfg or PreferenceConfig()

    # --------------------------------------------------------
    # Context signature
    # --------------------------------------------------------

    def context_key_from_accounting(
        self,
        *,
        coherence: float,
        fragmentation: float,
        block_rate: float,
        notes: List[str],
    ) -> str:
        """
        Build a tiny structural context key.
        No semantics, no labels like 'wall'/'door'/'tv'.
        Only coarse bins.

        Bins:
          coherence: low/med/high
          frag: low/med/high
          block: low/med/high
          flags: presence of key notes
        """
        cbin = self._bin3(coherence)
        fbin = self._bin3(fragmentation)
        bbin = self._bin3(block_rate)

        flags: List[str] = []
        # Keep flags minimal; they become stable "kinds" of frames.
        if "persistent_blocking" in notes:
            flags.append("pb")
        if "high_fragmentation" in notes:
            flags.append("hf")
        if "high_coherence" in notes:
            flags.append("hc")

        flag_str = "-".join(flags) if flags else "none"
        return f"c:{cbin}|f:{fbin}|b:{bbin}|{flag_str}"

    # --------------------------------------------------------
    # Update rule
    # --------------------------------------------------------

    def update(
        self,
        *,
        context_key: str,
        coherence: float,
        fragmentation: float,
        block_rate: float,
        prediction_error_l1: Optional[float],
    ) -> PreferenceUpdate:
        """
        Update preference for a context.

        Preference signal:
          + coherence (settles)
          - fragmentation (splits / noisy)
          - prediction error (mismatch)
          - persistent blocking (load proxy)

        Result is mapped into [-1, +1] and applied as a slow drift.
        """
        prev = self.store.get(context_key)

        pe = float(prediction_error_l1) if prediction_error_l1 is not None else 0.25
        pe = self._clip01(pe)

        coherence = self._clip01(coherence)
        fragmentation = self._clip01(fragmentation)
        block_rate = self._clip01(block_rate)

        # Stability score in [-1, +1]
        # Higher coherence improves; fragmentation/error/blocking reduce.
        stability = (
            self.cfg.w_coherence * coherence
            - self.cfg.w_frag * fragmentation
            - self.cfg.w_error * pe
            - self.cfg.w_blocking * block_rate
        )

        # Map stability from roughly [-1, +1] range into [-1, +1] cleanly
        # (stability may drift beyond; clamp)
        stability = self._clip(stability, -1.0, 1.0)

        # Decay preference slightly toward neutral each update
        decayed = prev * (1.0 - self.cfg.decay)

        # Apply update
        updated = decayed + self.cfg.lr * stability
        updated = self._clip(updated, self.cfg.clip_min, self.cfg.clip_max)

        self.store.set(context_key, updated)

        delta = updated - prev

        reason = self._reason(coherence, fragmentation, block_rate, pe)

        return PreferenceUpdate(
            context_key=context_key,
            previous=prev,
            updated=updated,
            delta=delta,
            reason=reason,
        )

    # --------------------------------------------------------
    # Helpers
    # --------------------------------------------------------

    @staticmethod
    def _clip(v: float, lo: float, hi: float) -> float:
        return max(lo, min(hi, float(v)))

    @staticmethod
    def _clip01(v: float) -> float:
        return max(0.0, min(1.0, float(v)))

    @staticmethod
    def _bin3(v01: float) -> str:
        v = max(0.0, min(1.0, float(v01)))
        if v < 0.34:
            return "low"
        if v < 0.67:
            return "med"
        return "high"

    @staticmethod
    def _reason(coh: float, frag: float, block: float, pe: float) -> str:
        # Simple textual label for logs/dashboards (still non-semantic)
        if coh > 0.7 and frag < 0.4 and pe < 0.4:
            return "settled"
        if block > 0.7:
            return "blocked_load"
        if frag > 0.7:
            return "fragmenting"
        if pe > 0.7:
            return "novel_mismatch"
        return "mixed"
