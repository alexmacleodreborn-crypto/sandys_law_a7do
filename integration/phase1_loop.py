from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from sandys_law_a7do.frames_toggle_types import FrameLike, FragmentLike  # optional shim (see note below)
from sandys_law_a7do.accounting.prediction_error import PredictionErrorEngine, Expectation


# ============================================================
# Phase 1 Outputs
# ============================================================

@dataclass(frozen=True)
class Phase1Entry:
    """
    What Phase 1 produced for this step.
    """
    signature: str
    coherence: float
    fragmentation: float
    prediction_error_l1: float


@dataclass(frozen=True)
class PreferenceUpdate:
    """
    Preference drift is not reward.
    It's structural affinity derived from repeatability & low error.
    """
    signature: str
    delta: float
    new_value: float


# ============================================================
# Phase 1 Loop
# ============================================================

class Phase1Loop:
    """
    Phase 1: Expectation + Prediction Error + Structural Preference Drift.

    Input:
      - frames: list of Frame objects (each has .fragments list)

    Output:
      - Phase1Entry
      - PreferenceUpdate (may be None in early phases)
    """

    def __init__(self) -> None:
        self.prediction = PredictionErrorEngine()
        self.expectation = Expectation()
        self._prefs: Dict[str, float] = {}  # signature -> [-1..+1] soft affinity

    # ----------------------------
    # Public API
    # ----------------------------

    def step(self, *, frames: List[FrameLike]) -> Tuple[Phase1Entry, Optional[PreferenceUpdate]]:
        # Flatten fragments from all frames
        recent: List[FragmentLike] = []
        for fr in frames:
            recent.extend(getattr(fr, "fragments", []))

        # Compute signature + simple coherence/fragmentation metrics
        signature, coherence, fragmentation = self._summarize(recent)

        # Prediction error (engine must be Fragment-based, not WorldEvent-based)
        pe = self.prediction.compute(
            recent_events=recent,
            expectation=self.expectation,
        )

        # Normalize interface from engine (support both dict or dataclass)
        pe_l1 = self._read_pe_l1(pe)

        # Update expectation with the newly observed structure
        self.expectation.update_from_observation(signature=signature, recent_events=recent)

        # Preference drift (structure affinity)
        pref_update = self._update_preference(signature=signature, prediction_error_l1=pe_l1, coherence=coherence)

        entry = Phase1Entry(
            signature=signature,
            coherence=coherence,
            fragmentation=fragmentation,
            prediction_error_l1=pe_l1,
        )
        return entry, pref_update

    def preferences(self) -> Dict[str, float]:
        return dict(self._prefs)

    # ----------------------------
    # Internals
    # ----------------------------

    def _summarize(self, fragments: List[FragmentLike]) -> Tuple[str, float, float]:
        """
        Create a stable signature for the structural content of recent fragments.
        No semantics: just kind + region keys + simple counts.
        """
        if not fragments:
            return ("∅", 0.0, 1.0)

        kind_counts: Dict[str, int] = {}
        region_counts: Dict[str, int] = {}

        for f in fragments:
            k = str(getattr(f, "kind", "unknown"))
            kind_counts[k] = kind_counts.get(k, 0) + 1

            payload = getattr(f, "payload", {}) or {}
            region = payload.get("region")
            if region is not None:
                r = str(region)
                region_counts[r] = region_counts.get(r, 0) + 1

        # Signature = sorted counts (deterministic)
        kinds = ",".join([f"{k}:{kind_counts[k]}" for k in sorted(kind_counts.keys())])
        regs = ",".join([f"{r}:{region_counts[r]}" for r in sorted(region_counts.keys())]) if region_counts else "none"
        signature = f"k[{kinds}]|r[{regs}]"

        # Coherence = concentration of dominant kind (simple, stable)
        total = sum(kind_counts.values())
        dominant = max(kind_counts.values())
        coherence = float(dominant) / float(total) if total > 0 else 0.0

        # Fragmentation = 1 - coherence (simple)
        fragmentation = max(0.0, min(1.0, 1.0 - coherence))

        return signature, coherence, fragmentation

    def _read_pe_l1(self, pe: object) -> float:
        """
        Accept either:
          - dict with 'prediction_error_l1'
          - dataclass with .prediction_error_l1
          - dict with 'l1'
          - dataclass with .l1
        """
        if pe is None:
            return 0.0
        if isinstance(pe, dict):
            if "prediction_error_l1" in pe:
                return float(pe["prediction_error_l1"])
            if "l1" in pe:
                return float(pe["l1"])
        # dataclass/object
        if hasattr(pe, "prediction_error_l1"):
            return float(getattr(pe, "prediction_error_l1"))
        if hasattr(pe, "l1"):
            return float(getattr(pe, "l1"))
        return 0.0

    def _update_preference(self, *, signature: str, prediction_error_l1: float, coherence: float) -> Optional[PreferenceUpdate]:
        """
        Preference is NOT reward.
        It is a drift toward repeatable, low-error structure.

        Rule:
          - lower error + higher coherence => positive drift
          - higher error => negative drift
        """
        old = float(self._prefs.get(signature, 0.0))

        # bounded soft update
        # (error in [0..1-ish], coherence in [0..1])
        delta = (0.08 * coherence) - (0.10 * min(1.0, max(0.0, prediction_error_l1)))
        new = max(-1.0, min(1.0, old + delta))
        self._prefs[signature] = new

        # Only emit update when it actually changes meaningfully
        if abs(delta) < 1e-6:
            return None
        return PreferenceUpdate(signature=signature, delta=float(delta), new_value=float(new))
