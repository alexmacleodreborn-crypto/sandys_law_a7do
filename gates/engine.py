# sandys_law_a7do/gates/engine.py
"""
Gate Engine — Phase 7.x (LOCKED)

Responsibilities:
- Maintain gate state
- Evaluate structural conditions
- Expose read-only gate snapshot
- NO mutation of world, memory, or actions
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# ✅ FIXED: relative import inside package
from .rules import (
    GateRule,
    GateDecision,
    default_gate_rules,
)


# =====================================================
# DATA STRUCTURES
# =====================================================

@dataclass
class GateState:
    """
    Internal mutable gate state.
    """
    score: float = 0.0
    decision: GateDecision = GateDecision.NEUTRAL
    reason: str = "init"


@dataclass(frozen=True)
class GateSnapshot:
    """
    Read-only snapshot for dashboards.
    """
    gates: Dict[str, Dict[str, object]]


# =====================================================
# ENGINE
# =====================================================

class GateEngine:
    """
    Structural gate evaluator.

    Gates DO NOT:
    - select actions
    - block perception
    - modify memory

    Gates ONLY:
    - score structure
    - expose readiness / suppression signals
    """

    def __init__(self, rules: Optional[List[GateRule]] = None):
        self.rules: List[GateRule] = rules or default_gate_rules()
        self._state: Dict[str, GateState] = {
            rule.name: GateState()
            for rule in self.rules
        }

    # -------------------------------------------------
    # EVALUATION
    # -------------------------------------------------

    def evaluate(
        self,
        *,
        coherence: float,
        fragmentation: float,
        stability: float,
        load: float,
    ) -> None:
        """
        Evaluate all gates using structural metrics.
        """

        for rule in self.rules:
            decision = rule.evaluate(
                coherence=coherence,
                fragmentation=fragmentation,
                stability=stability,
                load=load,
            )

            state = self._state[rule.name]
            state.score = decision.score
            state.decision = decision.decision
            state.reason = decision.reason

    # -------------------------------------------------
    # SNAPSHOT (READ-ONLY)
    # -------------------------------------------------

    def snapshot(self) -> GateSnapshot:
        """
        Return immutable snapshot for dashboards.
        """
        return GateSnapshot(
            gates={
                name: {
                    "score": gs.score,
                    "decision": gs.decision.value,
                    "reason": gs.reason,
                }
                for name, gs in self._state.items()
            }
        )