# sandys_law_a7do/engine/gate_engine.py

from sandys_law_a7do.gates.perception_gate import PerceptionGate
from sandys_law_a7do.gates.consolidation_gate import ConsolidationGate
from sandys_law_a7do.gates.education_gate import EducationGate
from sandys_law_a7do.gates.role_gate import RoleGate


class GateEngine:
    """
    Phase 7 — Gate Evaluation Engine

    - Pure evaluation
    - No side effects
    - No memory
    - No learning
    """

    def __init__(self):
        self.perception_gate = PerceptionGate()
        self.consolidation_gate = ConsolidationGate()
        self.education_gate = EducationGate()
        self.role_gate = RoleGate()

    def evaluate(self, *, state: dict) -> dict:
        """
        Evaluate all gates against current structural state.
        Returns a dict of GateDecision objects.
        """

        return {
            "perception": self.perception_gate.evaluate(
                block_rate=state.get("last_block_rate", 0.0),
                fragmentation=state.get("last_fragmentation", 0.0),
            ),
            "consolidation": self.consolidation_gate.evaluate(
                coherence=state.get("last_coherence", 0.0),
                fragmentation=state.get("last_fragmentation", 0.0),
            ),
            "education": self.education_gate.evaluate(
                readiness=state.get("readiness", 0.5),
                passed_exam=state.get("passed_exam", False),
            ),
            "role": self.role_gate.evaluate(
                role_name=state.get("role_name", "observer"),
                allowed_roles=state.get("allowed_roles", ["observer"]),
            ),
        }