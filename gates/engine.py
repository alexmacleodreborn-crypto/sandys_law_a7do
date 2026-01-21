# sandys_law_a7do/gates/engine.py

from dataclasses import dataclass
from typing import Dict, Optional

# ✅ IMPORT RULES FACTORY
from sandys_law_a7do.gates.rules import GateRule, default_gate_rules


# =====================================================
# GATE STATE
# =====================================================

@dataclass
class GateState:
    name: str
    score: float = 0.0
    pressure: float = 0.0
    open: bool = False
    reason: str = "init"


@dataclass
class GateSnapshot:
    gates: Dict[str, GateState]


# =====================================================
# GATE ENGINE
# =====================================================

class GateEngine:
    """
    Structural gating engine.

    - No learning
    - No reward
    - No action selection
    - Gates accumulate pressure and inertia
    """

    def __init__(self, rules: Optional[list[GateRule]] = None):
        # ✅ FIX: rules factory now exists
        self.rules: list[GateRule] = rules or default_gate_rules()

        self.gates: Dict[str, GateState] = {
            rule.name: GateState(name=rule.name)
            for rule in self.rules
        }

    # -------------------------------------------------
    # STEP
    # -------------------------------------------------

    def step(self, *, context: dict, tick: int):
        """
        Advance gate state by one tick.
        """
        for rule in self.rules:
            gate = self.gates[rule.name]

            decision = rule.evaluate(
                context=context,
                state=gate,
                tick=tick,
            )

            gate.score = decision.score
            gate.pressure = decision.pressure
            gate.open = decision.open
            gate.reason = decision.reason

    # -------------------------------------------------
    # SNAPSHOT
    # -------------------------------------------------

    def snapshot(self) -> GateSnapshot:
        """
        Read-only snapshot for dashboards.
        """
        return GateSnapshot(gates=dict(self.gates))