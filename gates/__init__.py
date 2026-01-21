# sandys_law_a7do/gates/__init__.py

# IMPORTANT:
# Do NOT import engine here to avoid circular imports.
# Engine must be imported directly where needed.

from .rules import GateRule, GateDecision, default_gate_rules

__all__ = [
    "GateRule",
    "GateDecision",
    "default_gate_rules",
]