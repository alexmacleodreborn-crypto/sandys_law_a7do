# sandys_law_a7do/gates/education_gate.py

from .base_gate import BaseGate, GateDecision


class EducationGate(BaseGate):
    """
    Allows educational progression when readiness is sufficient.
    """

    def evaluate(
        self,
        *,
        readiness: float,
        passed_exam: bool,
    ) -> GateDecision:
        if passed_exam and readiness >= 0.7:
            return GateDecision("allow", "exam_passed_and_ready")

        if readiness < 0.4:
            return GateDecision("block", "low_readiness")

        return GateDecision("defer", "awaiting_requirements")
