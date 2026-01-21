# sandys_law_a7do/gates/rules.py

from dataclasses import dataclass
from typing import Callable


@dataclass(frozen=True)
class GateRule:
    name: str
    weight: float
    threshold: float
    evaluator: Callable[[dict], float]


def default_gate_rules():
    return [
        GateRule(
            name="coherence_gate",
            weight=1.0,
            threshold=0.6,
            evaluator=lambda ctx: ctx.get("coherence", 0.0),
        ),
        GateRule(
            name="load_gate",
            weight=0.8,
            threshold=0.7,
            evaluator=lambda ctx: 1.0 - ctx.get("load", 0.0),
        ),
    ]