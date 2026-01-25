# sandys_law_a7do/scuttling/coupling/__init__.py

"""
Structural body coupling layer.

Defines how load and stability propagate between
body regions without cognition, reward, or planning.

This is a physical substrate for:
- reflexes
- local copilot
- embodiment invariants
"""

from .region import CoupledRegion
from .graph import CouplingGraph, CouplingEdge
from .propagate import propagate_once

__all__ = [
    "CoupledRegion",
    "CouplingGraph",
    "CouplingEdge",
    "propagate_once",
]