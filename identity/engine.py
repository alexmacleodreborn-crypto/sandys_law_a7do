from __future__ import annotations

from dataclasses import replace
from typing import Any, Optional

from sandys_law_a7do.identity.record import IdentityRecord
from sandys_law_a7do.identity.traits import TraitCrystallizer


class IdentityEngine:
    """
    Stage B enabled:
    - updates continuity metrics (coherence, fragmentation, confidence)
    - crystallizes traits from repeated stable traces
    """

    def __init__(self) -> None:
        self.traits = TraitCrystallizer()

    def update(
        self,
        identity: IdentityRecord,
        *,
        coherence: float,
        fragmentation: float,
        prediction_error: float,
        ownership_consistency: float,
        new_trace: Optional[Any] = None,
    ) -> IdentityRecord:
        # -----------------------------
        # Continuity / confidence update
        # (conservative: identity is stable, not twitchy)
        # -----------------------------
        c = float(coherence)
        f = float(fragmentation)
        pe = float(prediction_error)

        # Confidence heuristic:
        # - rises with coherence
        # - falls with prediction error
        # - bounded
        raw_conf = (0.60 * c) + (0.40 * (1.0 - min(1.0, pe)))
        raw_conf = max(0.0, min(1.0, raw_conf))

        # Preserve existing confidence inertia if present
        prev_conf = float(getattr(identity, "confidence", 0.2))
        new_conf = 0.70 * prev_conf + 0.30 * raw_conf

        # -----------------------------
        # Trait crystallization (Stage B)
        # -----------------------------
        traits_dict = dict(getattr(identity, "traits", {}) or {})

        if new_trace is not None:
            # We expect a trace-like object with:
            # signature, strength, frames_observed (or frames)
            sig = getattr(new_trace, "signature", None)
            strength = getattr(new_trace, "strength", None)

            if sig is not None and strength is not None:
                trait = self.traits.update(
                    signature=str(sig),
                    trace_strength=float(strength),
                    coherence=c,
                    prediction_error=pe,
                )
                if trait is not None:
                    traits_dict[trait.trait_id] = trait.to_dict()

        # -----------------------------
        # Write back updated identity
        # -----------------------------
        return replace(
            identity,
            coherence=c,
            fragmentation=f,
            confidence=new_conf,
            traits=traits_dict,
        )
