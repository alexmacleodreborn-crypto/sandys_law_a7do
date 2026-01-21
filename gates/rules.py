# sandys_law_a7do/gates/rules.py
"""
Gate Rules — Phase 7.x (LOCKED)

Defines:
- GateDecision enum
- GateRule interface
- Default structural gate rules

Gates:
- DO NOT select actions
- DO NOT write memory
- DO NOT modify perception
- ONLY score structural readiness
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


# =====================================================
# DECISIONS
# =====================================================

class GateDecision(Enum):
    OPEN = "open"
    HOLD = "hold"
    SUPPRESS = "suppress"
    NEUTRAL = "neutral"


# =====================================================
# RULE RESULT
# =====================================================

@dataclass(frozen=True)
class GateResult:
    score: float
    decision: GateDecision
    reason: str


# =====================================================
# RULE BASE
# =====================================================

class GateRule:
    """
    Base class for all gate rules.
    """

    name: str

    def evaluate(
        self,
        *,
        coherence: float,
        fragmentation: float,
        stability: float,
        load: float,
    ) -> GateResult:
        raise NotImplementedError


# =====================================================
# DEFAULT RULES
# =====================================================

class StabilityGate(GateRule):
    name = "stability"

    def evaluate(self, *, coherence, fragmentation, stability, load) -> GateResult:
        if stability >= 0.75:
            return GateResult(
                score=stability,
                decision=GateDecision.OPEN,
                reason="stable_structure",
            )
        if stability <= 0.4:
            return GateResult(
                score=stability,
                decision=GateDecision.SUPPRESS,
                reason="unstable_structure",
            )
        return GateResult(
            score=stability,
            decision=GateDecision.HOLD,
            reason="stability_transition",
        )


class LoadGate(GateRule):
    name = "load"

    def evaluate(self, *, coherence, fragmentation, stability, load) -> GateResult:
        if load >= 0.7:
            return GateResult(
                score=load,
                decision=GateDecision.SUPPRESS,
                reason="excess_load",
            )
        if load <= 0.3:
            return GateResult(
                score=1.0 - load,
                decision=GateDecision.OPEN,
                reason="low_load",
            )
        return GateResult(
            score=1.0 - load,
            decision=GateDecision.HOLD,
            reason="moderate_load",
        )


class CoherenceGate(GateRule):
    name = "coherence"

    def evaluate(self, *, coherence, fragmentation, stability, load) -> GateResult:
        if coherence >= 0.8:
            return GateResult(
                score=coherence,
                decision=GateDecision.OPEN,
                reason="high_coherence",
            )
        if coherence <= 0.4:
            return GateResult(
                score=coherence,
                decision=GateDecision.SUPPRESS,
                reason="low_coherence",
            )
        return GateResult(
            score=coherence,
            decision=GateDecision.HOLD,
            reason="coherence_transition",
        )


# =====================================================
# RULESET FACTORY
# =====================================================

def default_gate_rules() -> List[GateRule]:
    """
    Default gate set used by GateEngine.
    """
    return [
        StabilityGate(),
        LoadGate(),
        CoherenceGate(),
    ]