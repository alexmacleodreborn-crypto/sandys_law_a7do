from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


# ============================================================
# Reflex Types (PURE DATA — NO LOGIC)
# ============================================================

@dataclass(frozen=True)
class ReflexAction:
    name: str
    target_region: str
    intensity: float
    reason: str


@dataclass(frozen=True)
class ReflexResult:
    triggered: bool
    action: Optional[ReflexAction]
    load_delta: float
    stability_delta: float


@dataclass(frozen=True)
class CoupledReflexOutcome:
    triggered: bool
    dominant_action: Optional[ReflexAction]
    net_load_delta: float
    net_stability_delta: float
    unresolved_conflict: bool