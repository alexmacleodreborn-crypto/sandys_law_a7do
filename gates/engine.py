"""
Gate Engine — Phase 7.3 (STRUCTURAL, READ-ONLY)

Responsibilities:
- Evaluate gate rules against system snapshot
- Maintain internal gate scores
- Expose READ-ONLY snapshots for dashboards / downstream use

NO:
- control
- blocking
- routing
- action selection
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List

from sandys_law_a7do.gates.rules import GateRule, default_gate_rules


# --------------------------------------------------
# Gate State (internal, mutable)
# --------------------------------------------------

@dataclass
class GateState:
    """
    Internal gate state (scores only).
    """
    scores: Dict[str, float] = field(default_factory=dict)


# --------------------------------------------------
# Gate Snapshot (external, immutable)
# --------------------------------------------------

@dataclass(frozen=True)
class GateSnapshot:
    """
    Read-only gate snapshot.
    """
    scores: Dict[str, float]


# --------------------------------------------------
# Gate Engine
# --------------------------------------------------

class GateEngine:
    """
    Evaluates structural gates.

    IMPORTANT:
    - Gates do NOT block
    - Gates do NOT select
    - Gates only SCORE
    """

    def __init__(self, rules: List[GateRule] | None = None):
        self.rules: List[GateRule] = rules or list(default_gate_rules)
        self.state = GateState()

    # ----------------------------------------------
    # Evaluate gates against system snapshot
    # ----------------------------------------------

    def evaluate(self, system_snapshot: Dict[str, Any]) -> None:
        """
        Update internal gate scores from snapshot.
        """
        for rule in self.rules:
            try:
                score = float(rule.evaluator(system_snapshot))
            except Exception:
                score = 0.0

            # Clamp to [0, 1]
            score = max(0.0, min(1.0, score))
            self.state.scores[rule.name] = score

    # ----------------------------------------------
    # REQUIRED METHOD (THIS FIXES YOUR ERROR)
    # ----------------------------------------------

    def snapshot(self) -> GateSnapshot:
        """
        Return a read-only snapshot of gate scores.
        """
        return GateSnapshot(scores=dict(self.state.scores))