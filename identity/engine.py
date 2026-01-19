ffrom __future__ import annotations

from .record import IdentityRecord


class IdentityEngine:
    """
    Updates identity from structural learning signals.
    """

    def update(
        self,
        identity: IdentityRecord,
        *,
        coherence: float,
        fragmentation: float,
        prediction_error: float,
        ownership_consistency: float,
        new_trace: object | None = None,
    ) -> IdentityRecord:
        confidence = max(
            0.0,
            min(
                1.0,
                identity.confidence
                + (0.3 * coherence)
                - (0.2 * prediction_error)
                + (0.1 * ownership_consistency),
            ),
        )

        return IdentityRecord(
            identity_id=identity.identity_id,
            coherence=coherence,
            fragmentation=fragmentation,
            confidence=confidence,
            traits=dict(identity.traits),
        )
