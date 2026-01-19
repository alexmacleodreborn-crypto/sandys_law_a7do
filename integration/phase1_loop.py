from __future__ import annotations

from typing import List, Optional

from world.world_state import WorldEvent
from accounting.prediction_error import PredictionErrorEngine, Expectation
from accounting.accountant import Accountant, AccountantEntry
from mind.preference import PreferenceEngine, PreferenceUpdate


# ============================================================
# Phase 1 Integration Loop
#
# This is NOT a controller.
# This is NOT a policy.
#
# It is a structural analysis pipeline over frames.
# ============================================================


class Phase1Loop:
    """
    Minimal Phase 1 integration.

    Input:
      - frames: list of frames (each frame = list of WorldEvent)

    Output:
      - AccountantEntry
      - PreferenceUpdate (optional)
    """

    def __init__(
        self,
        *,
        preference_engine: Optional[PreferenceEngine] = None,
        prediction_engine: Optional[PredictionErrorEngine] = None,
    ) -> None:
        self.accountant = Accountant()
        self.prediction = prediction_engine or PredictionErrorEngine()
        self.preferences = preference_engine or PreferenceEngine()

        # Extremely conservative initial expectation
        self.expectation = Expectation(
            x_hat={
                "moved": 0.5,
                "blocked": 0.5,
                "blocked_by_wall": 0.25,
                "blocked_by_boundary": 0.25,
            }
        )

    # --------------------------------------------------------
    # Run one analysis step
    # --------------------------------------------------------

    def step(
        self,
        *,
        frames: List[List[WorldEvent]],
    ) -> tuple[AccountantEntry, PreferenceUpdate]:
        """
        Analyze frames → compute prediction error → update preference.

        Frames are assumed to be:
          - chronological
          - already gated
          - already deterministic
        """

        # Flatten recent events for prediction error
        recent_events: List[WorldEvent] = []
        for f in frames:
            recent_events.extend(f.fragments)

        # ---------------------------
        # Prediction error
        # ---------------------------

        pe = self.prediction.compute(
            recent_events=recent_events,
            expectation=self.expectation,
        )

        # ---------------------------
        # Accounting
        # ---------------------------

        entry = self.accountant.summarize(
            frames=frames,
            prediction_error=pe,
        )

        # ---------------------------
        # Context key
        # ---------------------------

        ctx = self.preferences.context_key_from_accounting(
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
            block_rate=entry.outcome_block_rate,
            notes=entry.notes,
        )

        # ---------------------------
        # Preference update
        # ---------------------------

        pref_update = self.preferences.update(
            context_key=ctx,
            coherence=entry.coherence,
            fragmentation=entry.fragmentation,
            block_rate=entry.outcome_block_rate,
            prediction_error_l1=entry.prediction_error_l1,
        )

        return entry, pref_update
