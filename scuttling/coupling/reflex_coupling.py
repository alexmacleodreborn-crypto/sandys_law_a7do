from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from sandys_law_a7do.scuttling.reflex import ReflexResult, ReflexAction


# ============================================================
# Coupled Outcome
#
# Result of combining multiple reflexes acting locally.
# This is STILL non-cognitive and non-symbolic.
# ============================================================

@dataclass(frozen=True)
class CoupledReflexOutcome:
    """
    Result of coupling multiple reflex results.
    """
    triggered: bool
    dominant_action: Optional[ReflexAction]

    net_load_delta: float          # combined load effect
    net_stability_delta: float     # combined stability effect

    unresolved_conflict: bool      # True if reflexes conflicted


# ============================================================
# Reflex Coupling Engine
# ============================================================

class ReflexCouplingEngine:
    """
    Combines multiple ReflexResults into a single structural outcome.

    This layer:
    - resolves conflicts
    - aggregates load/stability deltas
    - selects a dominant action if possible

    This layer does NOT:
    - store memory
    - gate actions
    - reason
    - plan
    """

    # Conservative caps to prevent runaway effects
    MAX_LOAD_REDUCTION = -0.6
    MAX_STABILITY_GAIN = +0.4

    def couple(
        self,
        *,
        results: List[ReflexResult],
    ) -> CoupledReflexOutcome:
        if not results:
            return CoupledReflexOutcome(
                triggered=False,
                dominant_action=None,
                net_load_delta=0.0,
                net_stability_delta=0.0,
                unresolved_conflict=False,
            )

        triggered_results = [r for r in results if r.triggered]

        if not triggered_results:
            return CoupledReflexOutcome(
                triggered=False,
                dominant_action=None,
                net_load_delta=0.0,
                net_stability_delta=0.0,
                unresolved_conflict=False,
            )

        # --------------------------------------------
        # Aggregate structural deltas
        # --------------------------------------------
        load_delta = sum(r.load_delta for r in triggered_results)
        stability_delta = sum(r.stability_delta for r in triggered_results)

        # Clamp conservatively
        load_delta = max(self.MAX_LOAD_REDUCTION, load_delta)
        stability_delta = min(self.MAX_STABILITY_GAIN, stability_delta)

        # --------------------------------------------
        # Resolve dominant action
        # --------------------------------------------
        actions = [r.action for r in triggered_results if r.action is not None]

        dominant_action: Optional[ReflexAction] = None
        unresolved_conflict = False

        if actions:
            # Sort by intensity (highest first)
            actions_sorted = sorted(
                actions,
                key=lambda a: a.intensity,
                reverse=True,
            )

            dominant_action = actions_sorted[0]

            # Detect conflicts:
            # Different actions targeting different regions
            target_regions = {a.target_region for a in actions_sorted}
            action_names = {a.name for a in actions_sorted}

            if len(target_regions) > 1 and len(action_names) > 1:
                unresolved_conflict = True

        return CoupledReflexOutcome(
            triggered=True,
            dominant_action=dominant_action,
            net_load_delta=load_delta,
            net_stability_delta=stability_delta,
            unresolved_conflict=unresolved_conflict,
        )