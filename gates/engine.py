# sandys_law_a7do/gates/engine.py
"""
Gate Engine — Phase 7.2 (STRUCTURAL, READ-ONLY)
"""

from typing import Dict

from sandys_law_a7do.gates.base_gate import GateDecision
from sandys_law_a7do.gates.gate_state import GateState

from sandys_law_a7do.gates.perception_gate import PerceptionGate
from sandys_law_a7do.gates.consolidation_gate import ConsolidationGate
from sandys_law_a7do.gates.education_gate import EducationGate
from sandys_law_a7do.gates.role_gate import RoleGate


class GateEngine:
    """
    Structural gate evaluation engine.
    """

    def __init__(self) -> None:
        self.perception_gate = PerceptionGate()
        self.consolidation_gate = ConsolidationGate()
        self.education_gate = EducationGate()
        self.role_gate = RoleGate()

    def evaluate(self, *, state: dict) -> GateState:
        decisions: Dict[str, GateDecision] = {}

        decisions["perception"] = self.perception_gate.evaluate(
            block_rate=float(state.get("last_block_rate", 0.0)),
            fragmentation=float(state.get("last_fragmentation", 0.0)),
        )

        decisions["consolidation"] = self.consolidation_gate.evaluate(
            coherence=float(state.get("last_coherence", 0.0)),
            fragmentation=float(state.get("last_fragmentation", 0.0)),
        )

        decisions["education"] = self.education_gate.evaluate(
            readiness=float(state.get("readiness", 0.5)),
            passed_exam=bool(state.get("passed_exam", False)),
        )

        decisions["role"] = self.role_gate.evaluate(
            role_name=state.get("role_name", "observer"),
            allowed_roles=state.get("allowed_roles", ["observer"]),
        )

        return GateState(decisions=decisions)