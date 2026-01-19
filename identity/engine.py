from __future__ import annotations

from dataclasses import replace
from typing import List, Optional

from .record import IdentityRecord
from memory.crystallizer import MemoryTrace


class IdentityEngine:
    """
    Updates IdentityRecord from structural signals.

    Inputs (all bounded):
    - coherence, fragmentation, prediction_error
    - embodiment ownership consistency signals (provided by caller)
    - memory trace formation events

    Doctrine:
    - slow drift
    - bounded values
    - no semantics
    """

    def __init__(
        self,
        *,
        lr_stability: float = 0.06,
        lr_novelty: float = 0.05,
        lr_integrity: float = 0.06,
        decay: float = 0.01,
    ) -> None:
        self.lr_stability = float(lr_stability)
        self.lr_novelty = float(lr_novelty)
        self.lr_integrity = float(lr_integrity)
        self.decay = float(decay)

    def update(
        self,
        record: IdentityRecord,
        *,
        coherence: float,
        fragmentation: float,
        prediction_error: Optional[float],
        ownership_consistency: float,
        new_trace: Optional[MemoryTrace],
    ) -> IdentityRecord:
        # Clamp inputs
        coherence = IdentityRecord.clamp01(coherence)
        fragmentation = IdentityRecord.clamp01(fragmentation)
        pe = IdentityRecord.clamp01(float(prediction_error) if prediction_error is not None else 0.25)
        ownership_consistency = IdentityRecord.clamp01(ownership_consistency)

        # Drift to neutral (prevents lock-in)
        stability = record.stability_index * (1.0 - self.decay)
        novelty = record.novelty_index * (1.0 - self.decay)
        integrity = record.embodiment_integrity * (1.0 - self.decay)

        # Stability increases with coherence and decreases with fragmentation + error
        stability_delta = self.lr_stability * (coherence - 0.5 * fragmentation - 0.5 * pe)
        stability = IdentityRecord.clamp01(stability + stability_delta)

        # Novelty increases with prediction error and fragmentation
        novelty_delta = self.lr_novelty * (0.7 * pe + 0.3 * fragmentation - 0.2 * coherence)
        novelty = IdentityRecord.clamp01(novelty + novelty_delta)

        # Embodiment integrity increases with consistent ownership
        integrity_delta = self.lr_integrity * (ownership_consistency - 0.5 * pe)
        integrity = IdentityRecord.clamp01(integrity + integrity_delta)

        commitments = list(record.commitments)
        if new_trace is not None:
            # Commitments are non-semantic tags of crystallized stable contexts
            tag = f"trace:{new_trace.signature}"
            if tag not in commitments:
                commitments.append(tag)

        return replace(
            record,
            stability_index=stability,
            novelty_index=novelty,
            embodiment_integrity=integrity,
            commitments=commitments,
        )