from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple


# ============================================================
# Phase 1 Outputs
# ============================================================

@dataclass(frozen=True)
class Phase1Entry:
    """
    Structural summary of a closed frame set.
    """
    signature: str
    coherence: float
    fragmentation: float
    prediction_error_l1: float


@dataclass(frozen=True)
class PreferenceUpdate:
    """
    Structural preference drift (NOT reward).
    """
    signature: str
    delta: float
    new_value: float


# ============================================================
# Prediction Error Engine (local, fragment-based)
# ============================================================

class PredictionErrorEngine:
    """
    Computes simple L1 prediction error over fragment structure.
    """

    def compute(self, *, recent_events: List[object], expectation: Dict[str, float]) -> float:
        if not recent_events:
            return 0.0

        counts: Dict[str, int] = {}
        for f in recent_events:
            kind = getattr(f, "kind", "unknown")
            counts[kind] = counts.get(kind, 0) + 1

        total = sum(counts.values())
        error = 0.0

        for kind, observed in counts.items():
            expected = expectation.get(kind, 0.0)
            error += abs((observed / total) - expected)

        return float(error)


# ============================================================
# Phase 1 Loop
# ============================================================

class Phase1Loop:
    """
    Phase 1: Structure → Expectation → Prediction Error → Preference Drift
    """

    def __init__(self) -> None:
        self.prediction = PredictionErrorEngine()
        self.expectation: Dict[str, float] = {}
        self._prefs: Dict[str, float] = {}

    # ----------------------------
    # Public API
    # ----------------------------

    def step(self, *, frames: List[object]) -> Tuple[Phase1Entry, Optional[PreferenceUpdate]]:
        fragments: List[object] = []
        for fr in frames:
            fragments.extend(getattr(fr, "fragments", []))

        signature, coherence, fragmentation = self._summarize(fragments)

        pe_l1 = self.prediction.compute(
            recent_events=fragments,
            expectation=self.expectation,
        )

        # Update expectation
        self._update_expectation(fragments)

        pref_update = self._update_preference(signature, coherence, pe_l1)

        entry = Phase1Entry(
            signature=signature,
            coherence=coherence,
            fragmentation=fragmentation,
            prediction_error_l1=pe_l1,
        )

        return entry, pref_update

    # ----------------------------
    # Internals
    # ----------------------------

    def _summarize(self, fragments: List[object]) -> Tuple[str, float, float]:
        if not fragments:
            return ("∅", 0.0, 1.0)

        counts: Dict[str, int] = {}
        for f in fragments:
            kind = getattr(f, "kind", "unknown")
            counts[kind] = counts.get(kind, 0) + 1

        total = sum(counts.values())
        dominant = max(counts.values())

        coherence = dominant / total
        fragmentation = 1.0 - coherence

        sig = ",".join(f"{k}:{counts[k]}" for k in sorted(counts.keys()))
        signature = f"struct[{sig}]"

        return signature, float(coherence), float(fragmentation)

    def _update_expectation(self, fragments: List[object]) -> None:
        counts: Dict[str, int] = {}
        for f in fragments:
            kind = getattr(f, "kind", "unknown")
            counts[kind] = counts.get(kind, 0) + 1

        total = sum(counts.values())
        if total == 0:
            return

        for kind, c in counts.items():
            self.expectation[kind] = c / total

    def _update_preference(
        self,
        signature: str,
        coherence: float,
        prediction_error: float,
    ) -> Optional[PreferenceUpdate]:
        old = self._prefs.get(signature, 0.0)

        delta = (0.1 * coherence) - (0.1 * prediction_error)
        new = max(-1.0, min(1.0, old + delta))

        self._prefs[signature] = new

        if abs(delta) < 1e-6:
            return None

        return PreferenceUpdate(
            signature=signature,
            delta=float(delta),
            new_value=float(new),
        )
