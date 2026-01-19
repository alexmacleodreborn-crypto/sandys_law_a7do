from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from sandys_law_a7do.integration.phase1_loop import (
    Phase1Loop,
    Phase1Entry,
    PreferenceUpdate,
)
from sandys_law_a7do.accounting.preference_field import PreferenceField
from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace


@dataclass
class Phase2Result:
    entry: Phase1Entry
    preference_update: PreferenceUpdate
    trace: MemoryTrace


class Phase2Loop:
    """
    Phase 2:
    - Integrates Phase 1 structural metrics
    - Crystallizes memory traces
    - Updates Preference Field (Stage C1)
    """

    def __init__(self) -> None:
        self.phase1 = Phase1Loop()
        self.memory = StructuralMemory()
        self.preference_field = PreferenceField()

    # --------------------------------------------------------

    def step(self, frames: List) -> Tuple[Phase1Entry, PreferenceUpdate, MemoryTrace]:
        """
        Process closed frames.
        """
        # -------- Phase 1 --------
        entry, pref_update = self.phase1.step(frames)

        # -------- Memory --------
        trace = self.memory.integrate(
            frames=frames,
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
        )

        # -------- Stage C1: Preference Field --------
        signatures = set(trace.signatures)

        for sig in signatures:
            self.preference_field.update(
                signature=sig,
                prediction_error=entry.prediction_error_l1,
            )

        self.preference_field.decay_unseen(signatures)

        return entry, pref_update, trace
