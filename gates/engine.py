# sandys_law_a7do/gates/engine.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional

from sandys_law_a7do.gates.rules import GateRule, default_gate_rules


# =====================================================
# Gate State Containers
# =====================================================

@dataclass(frozen=True)
class GateState:
    name: str
    score: float
    threshold: float
    open: bool


@dataclass(frozen=True)
class GateSnapshot:
    gates: Dict[str, GateState]

    def open_gates(self) -> List[str]:
        return [k for k, g in self.gates.items() if g.open]


# =====================================================
# Gate Engine
# =====================================================

class GateEngine:
    """
    Structural gate evaluator.

    - No memory
    - No learning
    - No decisions
    - Only computes openness from structural metrics
    """

    def __init__(self, rules: Optional[List[GateRule]] = None) -> None:
        self.rules: List[GateRule] = rules or default_gate_rules()
        self._last_snapshot: Optional[GateSnapshot] = None

    # -------------------------------------------------
    # Evaluation
    # -------------------------------------------------

    def evaluate(self, context: Dict[str, float]) -> GateSnapshot:
        gates: Dict[str, GateState] = {}

        for rule in self.rules:
            try:
                score = float(rule.evaluator(context))
            except Exception:
                score = 0.0

            open_ = score >= rule.threshold

            gates[rule.name] = GateState(
                name=rule.name,
                score=score,
                threshold=rule.threshold,
                open=open_,
            )

        snap = GateSnapshot(gates=gates)
        self._last_snapshot = snap
        return snap

    # -------------------------------------------------
    # Snapshot access
    # -------------------------------------------------

    def snapshot(self) -> Optional[GateSnapshot]:
        return self._last_snapshot