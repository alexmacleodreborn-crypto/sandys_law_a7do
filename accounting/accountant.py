# accountant/accountant.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from world.world_state import WorldEvent, WorldEventType
from accounting.prediction_error import PredictionErrorResult


# ============================================================
# Accountant Doctrine
#
# - Accountant observes events
# - Accountant does NOT decide
# - Accountant does NOT reward
# - Accountant does NOT remember semantically
#
# It produces STRUCTURAL METRICS ONLY.
# ============================================================


@dataclass
class AccountantEntry:
    """
    A single accounting snapshot over a frame window.

    These are *structural invariants* used later by:
    - memory formation
    - preference formation
    - embodiment confidence
    """

    # Frame accounting
    frame_count: int
    event_count: int

    # Event composition
    obs_count: int
    act_count: int
    out_count: int
    sys_count: int
    int_count: int

    # Flux / stability
    outcome_success_rate: float
    outcome_block_rate: float

    # Fragmentation & coherence
    fragmentation: float          # many unrelated events
    coherence: float              # outcomes tied to actions

    # Prediction error (structural)
    prediction_error_l1: Optional[float] = None

    # Notes (machine-readable tags)
    notes: List[str] = field(default_factory=list)

    # --------------------------------------------------------
    # NEW: Read-only embodiment context (no authority)
    # --------------------------------------------------------
    embodiment: Optional[Dict[str, float]] = None


class Accountant:
    """
    Deterministic structural accounting engine.

    Input:
      - a bounded list of WorldEvents (chronological)
      - optional prediction error result
      - optional embodiment summary (read-only)

    Output:
      - AccountantEntry
    """

    def __init__(self) -> None:
        pass

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def summarize(
        self,
        *,
        frames: List[List[WorldEvent]],
        prediction_error: Optional[PredictionErrorResult] = None,
        embodiment: Optional[Dict[str, float]] = None,
    ) -> AccountantEntry:
        """
        Summarize a set of frames.

        frames = list of frames
        each frame = list of WorldEvents
        """

        all_events: List[WorldEvent] = []
        for f in frames:
            all_events.extend(f)

        frame_count = len(frames)
        event_count = len(all_events)

        obs = act = out = sys = intr = 0
        success = block = 0
        linked_outcomes = 0

        # ----------------------------------------------------
        # Event counting
        # ----------------------------------------------------

        for e in all_events:
            if e.type == WorldEventType.OBSERVATION:
                obs += 1
            elif e.type == WorldEventType.ACTION:
                act += 1
            elif e.type == WorldEventType.OUTCOME:
                out += 1
                if e.name == "moved":
                    success += 1
                elif e.name == "blocked":
                    block += 1
                if e.parent_id is not None:
                    linked_outcomes += 1
            elif e.type == WorldEventType.SYSTEM:
                sys += 1
            elif e.type == WorldEventType.INTERNAL:
                intr += 1

        # ----------------------------------------------------
        # Rates
        # ----------------------------------------------------

        outcome_total = max(1, out)
        success_rate = success / outcome_total
        block_rate = block / outcome_total

        # ----------------------------------------------------
        # Fragmentation & coherence
        # ----------------------------------------------------

        fragmentation = self._clip01(event_count / max(1, frame_count * 8))
        coherence = self._clip01(linked_outcomes / max(1, out))

        notes: List[str] = []

        if fragmentation > 0.7:
            notes.append("high_fragmentation")
        if coherence > 0.7:
            notes.append("high_coherence")
        if success_rate > 0.7:
            notes.append("stable_outcomes")
        if block_rate > 0.7:
            notes.append("persistent_blocking")

        pe = prediction_error.error_l1 if prediction_error else None

        return AccountantEntry(
            frame_count=frame_count,
            event_count=event_count,
            obs_count=obs,
            act_count=act,
            out_count=out,
            sys_count=sys,
            int_count=intr,
            outcome_success_rate=success_rate,
            outcome_block_rate=block_rate,
            fragmentation=fragmentation,
            coherence=coherence,
            prediction_error_l1=pe,
            notes=notes,
            embodiment=embodiment,  # <-- pass-through only
        )

    # --------------------------------------------------------
    # Utils
    # --------------------------------------------------------

    @staticmethod
    def _clip01(v: float) -> float:
        if v < 0.0:
            return 0.0
        if v > 1.0:
            return 1.0
        return float(v)