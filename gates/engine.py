# sandys_law_a7do/gates/engine.py
"""
Gate Engine — Phase 7.3 (READ-ONLY)

Evaluates cognitive gates without enforcing them.
No mutation. No routing. No blocking.
"""

from dataclasses import dataclass
from typing import Dict, List

from sandys_law_a7do.gates.base_gate import BaseGate
from sandys_law_a7do.gates.perception_gate import PerceptionGate
from sandys_law_a7do.gates.consolidation_gate import ConsolidationGate
from sandys_law_a7do.gates.education_gate import EducationGate
from sandys_law_a7do.gates.role_gate import RoleGate


# --------------------------------------------------
# DATA STRUCTURES
# --------------------------------------------------

@dataclass(frozen=True)
class GateState:
    name: str
    score: float
    open: bool
    reason: str


@dataclass(frozen=True)
class GateSnapshot:
    states: Dict[str, GateState]


# --------------------------------------------------
# ENGINE
# --------------------------------------------------

class GateEngine:
    """
    Evaluates all gates using current system state.

    READ-ONLY:
    - Does not block
    - Does not mutate
    - Does not route
    """

    def __init__(self) -> None:
        self.gates: List[BaseGate] = [
            PerceptionGate(),
            ConsolidationGate(),
            EducationGate(),
            RoleGate(),
        ]

    def evaluate(self, state: dict) -> GateSnapshot:
        states: Dict[str, GateState] = {}

        for gate in self.gates:
            result = gate.evaluate(state)

            states[gate.name] = GateState(
                name=gate.name,
                score=float(result.score),
                open=bool(result.open),
                reason=str(result.reason),
            )

        return GateSnapshot(states=states)