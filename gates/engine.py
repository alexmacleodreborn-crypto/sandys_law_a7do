# sandys_law_a7do/gates/engine.py
"""
Gate Engine — Phase 7.2 (STRUCTURAL)

Responsibilities:
- Evaluate all registered gates
- Produce a GateState snapshot
- NO mutation
- NO persistence
- NO enforcement

GateState is:
- Derived
- Read-only
- Recomputed each evaluation
"""

from typing import Dict

from sandys_law_a7do.gates.base_gate import GateDecision
from sandys_law_a7do.gates.gate_state import GateState

from sandys_law_a7do.gates.perception_gate import PerceptionGate
from sandys_law_a7do.gates.consolidation_gate import ConsolidationGate
from sandys_law_a7do.gates.education_gate import EducationGate
from sandys_law_a7do.gates.role_gate import RoleGate


class Engine:
    """
    Structural gate evaluation engine.

    This engine:
    - Reads system state
    - Evaluates each gate independently
    - Returns a GateState snapshot
    """

    def __init__(self) -> None:
        self.perception_gate = PerceptionGate()
        self.consolidation_gate = ConsolidationGate()
        self.education_gate = EducationGate()
        self.role_gate = RoleGate()

    # --------------------------------------------------
    # MAIN ENTRYPOINT
    # --------------------------------------------------

    def evaluate(self, *, state: dict) -> GateState:
        """
        Evaluate all gates against current system state.

        Returns:
            GateState (read-only snapshot)
        """

        decisions: Dict[str, GateDecision] = {}

        # ----------------------------------------------
        # PERCEPTION GATE
        # ----------------------------------------------
        decisions["perception"] = self.perception_gate.evaluate(
            block_rate=float(state.get("last_block_rate", 0.0)),
            fragmentation=float(state.get("last_fragmentation", 0.0)),
        )

        # ----------------------------------------------
        # CONSOLIDATION GATE
        # ----------------------------------------------
        decisions["consolidation"] = self.consolidation_gate.evaluate(
            coherence=float(state.get("last_coherence", 0.0)),
            fragmentation=float(state.get("last_fragmentation", 0.0)),
        )

        # ----------------------------------------------
        # EDUCATION GATE
        # ----------------------------------------------
        decisions["education"] = self.education_gate.evaluate(
            readiness=float(state.get("readiness", 0.5)),
            passed_exam=bool(state.get("passed_exam", False)),
        )

        # ----------------------------------------------
        # ROLE GATE
        # ----------------------------------------------
        decisions["role"] = self.role_gate.evaluate(
            role_name=state.get("role_name", "observer"),
            allowed_roles=state.get("allowed_roles", ["observer"]),
        )

        # ----------------------------------------------
        # RETURN STRUCTURAL SNAPSHOT
        # ----------------------------------------------
        return GateState(decisions=decisions)