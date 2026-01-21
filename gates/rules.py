"""
Gate Rules — Phase 7.x (STRUCTURAL ONLY)

Defines:
- GateRule: declarative structural gate condition
- default_gate_rules: conservative baseline ruleset

IMPORTANT:
- No actions
- No control
- No blocking yet
- Gates only OBSERVE and SCORE
"""

from dataclasses import dataclass
from typing import Callable, Dict, Any, List


# --------------------------------------------------
# Gate Rule
# --------------------------------------------------

@dataclass(frozen=True)
class GateRule:
    """
    A structural gate rule.

    Evaluates a snapshot and returns a gate score in [0.0, 1.0].
    """
    name: str
    description: str
    evaluator: Callable[[Dict[str, Any]], float]


# --------------------------------------------------
# Default Gate Rules (VERY conservative)
# --------------------------------------------------

def _always_open(snapshot: Dict[str, Any]) -> float:
    return 1.0


def _low_fragmentation(snapshot: Dict[str, Any]) -> float:
    Z = snapshot.get("metrics", {}).get("Z", 0.0)
    return max(0.0, min(1.0, 1.0 - Z))


def _high_coherence(snapshot: Dict[str, Any]) -> float:
    c = snapshot.get("metrics", {}).get("Coherence", 0.0)
    return max(0.0, min(1.0, c))


default_gate_rules: List[GateRule] = [
    GateRule(
        name="always_open",
        description="Baseline gate — always open",
        evaluator=_always_open,
    ),
    GateRule(
        name="low_fragmentation",
        description="Prefers low fragmentation states",
        evaluator=_low_fragmentation,
    ),
    GateRule(
        name="high_coherence",
        description="Prefers high coherence states",
        evaluator=_high_coherence,
    ),
]