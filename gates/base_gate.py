# sandys_law_a7do/gates/base_gate.py

from dataclasses import dataclass
from typing import Literal


GateState = Literal["allow", "block", "defer"]


@dataclass(frozen=True)
class GateDecision:
    state: GateState
    reason: str


class BaseGate:
    """
    Base class for all gates.
    Gates evaluate conditions and emit a decision.
    """

    def evaluate(self, **inputs) -> GateDecision:
        raise NotImplementedError("Gate must implement evaluate()")
