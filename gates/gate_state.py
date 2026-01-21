# sandys_law_a7do/gates/gate_state.py

from dataclasses import dataclass
from typing import Dict

from .base_gate import GateDecision


@dataclass(frozen=True)
class GateState:
    """
    Snapshot of all gate decisions at a given moment.

    - Read-only
    - No persistence
    - Recomputed every evaluation
    """

    decisions: Dict[str, GateDecision]

    def allowed(self, gate_name: str) -> bool:
        d = self.decisions.get(gate_name)
        return d is not None and d.state == "allow"

    def blocked(self, gate_name: str) -> bool:
        d = self.decisions.get(gate_name)
        return d is not None and d.state == "block"

    def deferred(self, gate_name: str) -> bool:
        d = self.decisions.get(gate_name)
        return d is not None and d.state == "defer"