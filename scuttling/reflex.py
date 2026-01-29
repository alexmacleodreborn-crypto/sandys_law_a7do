"""
Reflex system façade.

This module exposes the reflex system as a single import point.
"""

from scuttling.coupling.reflex_buffer import ReflexBuffer
from scuttling.coupling.reflex_coupling import (
    ReflexCouplingEngine,
    CoupledReflexOutcome,
)

__all__ = [
    "ReflexBuffer",
    "ReflexCouplingEngine",
    "CoupledReflexOutcome",
]