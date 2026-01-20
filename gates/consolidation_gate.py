# sandys_law_a7do/gates/consolidation_gate.py

from .base_gate import BaseGate, GateDecision


class ConsolidationGate(BaseGate):
    """
    Allows consolidation only when structure is stable.
    """

    def evaluate(
        self,
        *,
        coherence: float,
        fragmentation: float,
    ) -> GateDecision:
        if coherence > 0.6 and fragmentation < 0.4:
            return GateDecision("allow", "stable_structure")

        if fragmentation > 0.7:
            return GateDecision("block", "excessive_fragmentation")

        return GateDecision("defer", "insufficient_stability")
