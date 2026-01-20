# tests/test_gates.py

from gates.consolidation_gate import ConsolidationGate
from gates.perception_gate import PerceptionGate


def test_consolidation_gate_returns_decision():
    gate = ConsolidationGate()
    decision = gate.evaluate(coherence=0.8, fragmentation=0.2)
    assert decision.state in ("allow", "block", "defer")


def test_perception_gate_blocks_on_overload():
    gate = PerceptionGate()
    decision = gate.evaluate(block_rate=0.9, fragmentation=0.1)
    assert decision.state == "block"
