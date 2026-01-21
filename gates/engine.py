# sandys_law_a7do/gates/engine.py

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Any, List

from sandys_law_a7do.gates.rules import GateRule, default_gate_rules


# =====================================================
# Gate State (Phase 7.4)
# =====================================================

@dataclass
class GateState:
    open: bool
    score: float          # ∈ [0,1] inertia
    pressure: float       # instantaneous load
    reason: str
    last_tick: int


@dataclass
class GateSnapshot:
    gates: Dict[str, GateState]


# =====================================================
# Gate Engine
# =====================================================

class GateEngine:
    """
    Phase 7.4 — Stateful gates with inertia.

    - Gates evaluate every tick
    - Gates accumulate pressure when blocking
    - Score drifts slowly, bounded
    - NO reward
    - NO preference
    - NO memory
    """

    def __init__(self, rules: List[GateRule] | None = None):
        self.rules = rules or default_gate_rules()
        self._states: Dict[str, GateState] = {}

    # -------------------------------------------------

    def step(self, *, context: Dict[str, Any], tick: int) -> None:
        for rule in self.rules:
            name = rule.name
            allowed, reason = rule.evaluate(context)

            prev = self._states.get(
                name,
                GateState(
                    open=True,
                    score=0.0,
                    pressure=0.0,
                    reason="init",
                    last_tick=tick,
                ),
            )

            # ------------------------------
            # Pressure update
            # ------------------------------
            if allowed:
                pressure = max(0.0, prev.pressure * 0.7)
            else:
                pressure = min(1.0, prev.pressure + 0.15)

            # ------------------------------
            # Score inertia update
            # ------------------------------
            if not allowed:
                score = min(1.0, prev.score + 0.05)
            else:
                score = max(0.0, prev.score * 0.95)

            self._states[name] = GateState(
                open=allowed,
                score=score,
                pressure=pressure,
                reason=reason,
                last_tick=tick,
            )

    # -------------------------------------------------

    def snapshot(self) -> GateSnapshot:
        return GateSnapshot(gates=dict(self._states))