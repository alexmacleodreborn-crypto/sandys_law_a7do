# sandys_law_a7do/gates/perception_gate.py

from .base_gate import BaseGate, GateDecision


class PerceptionGate(BaseGate):
    """
    Regulates perception flow based on load.
    """

    def evaluate(
        self,
        *,
        block_rate: float,
        fragmentation: float,
    ) -> GateDecision:
        if block_rate > 0.8:
            return GateDecision("block", "perceptual_overload")

        if fragmentation > 0.6:
            return GateDecision("defer", "fragmented_input")

        return GateDecision("allow", "normal_flow")
