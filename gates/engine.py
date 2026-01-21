# sandys_law_a7do/gates/rules.py

from dataclasses import dataclass
from typing import Callable, Dict


# =====================================================
# GATE DECISION
# =====================================================

@dataclass
class GateDecision:
    score: float
    pressure: float
    open: bool
    reason: str


# =====================================================
# GATE RULE
# =====================================================

@dataclass
class GateRule:
    """
    Structural gate rule.

    Rules do NOT:
    - select actions
    - learn
    - store memory
    """

    name: str
    evaluator: Callable[[Dict, float, int], GateDecision]

    def evaluate(self, *, context: Dict, state, tick: int) -> GateDecision:
        return self.evaluator(context, state, tick)


# =====================================================
# DEFAULT GATE RULES (FACTORY)
# =====================================================

def default_gate_rules() -> list[GateRule]:
    """
    Canonical gate set.
    These gates operate ONLY on structural metrics.
    """

    def perception_gate(ctx, state, tick):
        coherence = float(ctx.get("coherence", 0.0))
        pressure = state.pressure + (0.1 if coherence < 0.4 else -0.05)

        pressure = max(0.0, min(1.0, pressure))
        open_gate = pressure < 0.6

        return GateDecision(
            score=coherence,
            pressure=pressure,
            open=open_gate,
            reason="low_coherence" if not open_gate else "stable",
        )

    def load_gate(ctx, state, tick):
        load = float(ctx.get("load", 0.0))
        pressure = state.pressure + load * 0.1
        pressure = max(0.0, min(1.0, pressure))

        return GateDecision(
            score=1.0 - load,
            pressure=pressure,
            open=pressure < 0.7,
            reason="high_load" if pressure >= 0.7 else "ok",
        )

    return [
        GateRule(name="perception", evaluator=perception_gate),
        GateRule(name="load", evaluator=load_gate),
    ]