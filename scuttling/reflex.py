"""
Reflex system façade.

Exports reflex components without causing circular imports.
"""

from scuttling.coupling.reflex_buffer import ReflexBuffer
from scuttling.coupling.reflex_coupling import ReflexCouplingEngine
from scuttling.reflex_types import (
    ReflexResult,
    ReflexAction,
    CoupledReflexOutcome,
)

__all__ = [
    "ReflexBuffer",
    "ReflexCouplingEngine",
    "ReflexResult",
    "ReflexAction",
    "CoupledReflexOutcome",
]