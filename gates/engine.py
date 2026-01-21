# sandys_law_a7do/gates/engine.py
"""
Gate Engine — Phase 7 (LOCKED)

Responsibilities:
- Evaluate structural gate rules
- Maintain gate state
- Expose snapshot for dashboards
- NO action selection
- NO mutation outside engine
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

from sandys_law_a7do.gates.rules import (
    GateRule,
    GateDecision,
    default_gate_rules,
)


# =====================================================
# DATA MODELS
# =====================================================

@dataclass(frozen=True)
class GateState:
    name: str
    score: float
    threshold: float
    open: bool
    reason: str


@dataclass(frozen=True)
class GateSnapshot:
    gates: Dict[str, GateState]


# =====================================================
# ENGINE
# =====================================================

class GateEngine:
    """
    Structural gating engine.

    Inputs:
    - coherence
    - fragmentation
    - stability
    - load

    Output:
    - GateSnapshot
    """

    def __init__(self, rules: Optional[List[GateRule]] = None):
        self.rules: List[GateRule] = rules or default_gate_rules()
        self._last_snapshot: Optional[GateSnapshot] = None

    # -------------------------------------------------
    # EVALUATION (CALLED ON FRAME CLOSE)
    # -------------------------------------------------

    def evaluate(
        self,
        *,
        coherence: float,
        fragmentation: float,
        stability: float,
        load: float,
    ) -> GateSnapshot:
        """
        Evaluate all gate rules against current structural state.
        """

        gate_states: Dict[str, GateState] = {}

        for rule in self.rules:
            decision: GateDecision = rule.evaluate(
                coherence=coherence,
                fragmentation=fragmentation,
                stability=stability,
                load=load,
            )

            gate_states[rule.name] = GateState(
                name=rule.name,
                score=decision.score,
                threshold=decision.threshold,
                open=decision.open,
                reason=decision.reason,
            )

        snapshot = GateSnapshot(gates=gate_states)
        self._last_snapshot = snapshot
        return snapshot

    # -------------------------------------------------
    # SNAPSHOT (SAFE READ)
    # -------------------------------------------------

    def snapshot(self) -> Optional[GateSnapshot]:
        """
        Return last evaluated snapshot.

        May be None until first evaluation.
        """
        return self._last_snapshot