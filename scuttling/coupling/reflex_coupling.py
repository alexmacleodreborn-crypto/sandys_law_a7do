from __future__ import annotations
from typing import List, Optional

from scuttling.reflex_types import (
    ReflexResult,
    ReflexAction,
    CoupledReflexOutcome,
)


class ReflexCouplingEngine:
    """
    Combines multiple ReflexResults into a single structural outcome.
    """

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

        triggered = [r for r in results if r.triggered]
        if not triggered:
            return CoupledReflexOutcome(
                triggered=False,
                dominant_action=None,
                net_load_delta=0.0,
                net_stability_delta=0.0,
                unresolved_conflict=False,
            )

        load_delta = max(
            self.MAX_LOAD_REDUCTION,
            sum(r.load_delta for r in triggered),
        )

        stability_delta = min(
            self.MAX_STABILITY_GAIN,
            sum(r.stability_delta for r in triggered),
        )

        actions = [r.action for r in triggered if r.action]
        dominant_action: Optional[ReflexAction] = None
        unresolved_conflict = False

        if actions:
            actions = sorted(actions, key=lambda a: a.intensity, reverse=True)
            dominant_action = actions[0]

            regions = {a.target_region for a in actions}
            names = {a.name for a in actions}
            unresolved_conflict = len(regions) > 1 and len(names) > 1

        return CoupledReflexOutcome(
            triggered=True,
            dominant_action=dominant_action,
            net_load_delta=load_delta,
            net_stability_delta=stability_delta,
            unresolved_conflict=unresolved_conflict,
        )