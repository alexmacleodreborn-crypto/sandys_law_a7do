from __future__ import annotations

from typing import List, Optional

from world.world_state import WorldEvent
from integration.phase1_loop import Phase1Loop
from memory.crystallizer import MemoryCrystallizer, MemoryTrace


# ============================================================
# Phase 2 Integration Loop
#
# Phase 1:
#   Frames → Prediction → Accounting → Preference
#
# Phase 2:
#   Preference → Structural Memory (Crystallization)
#
# This layer still does NOT:
#   - choose actions
#   - modify the world
#   - inject semantics
# ============================================================


class Phase2Loop:
    """
    Phase 2 wrapper around Phase 1.

    Adds memory crystallization as a passive observer.
    """

    def __init__(
        self,
        *,
        crystallizer: Optional[MemoryCrystallizer] = None,
    ) -> None:
        self.phase1 = Phase1Loop()
        self.memory = crystallizer or MemoryCrystallizer()

        # Most recent crystallization (for UI)
        self.last_trace: Optional[MemoryTrace] = None

    # --------------------------------------------------------
    # Step
    # --------------------------------------------------------

    def step(
        self,
        *,
        frames: List[List[WorldEvent]],
    ):
        """
        Run Phase 1, then attempt memory crystallization.
        """

        entry, pref_update = self.phase1.step(frames=frames)

        trace = self.memory.observe(
            context_key=pref_update.context_key,
            preference_value=pref_update.updated,
        )

        if trace is not None:
            self.last_trace = trace

        return entry, pref_update, trace
