# genesis/prebirth/phases.py

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum, auto


class PrebirthPhase(Enum):
    INSEMINATION = auto()
    NEURAL_PLATE = auto()
    CORE_FORMATION = auto()
    LIMB_BUDS = auto()
    LIMB_EXTENSION = auto()
    PRE_BIRTH_STABLE = auto()


@dataclass(frozen=True)
class PhaseGate:
    phase: PrebirthPhase
    min_ticks: int


# Canonical developmental schedule (conservative)
PHASE_SCHEDULE = [
    PhaseGate(PrebirthPhase.INSEMINATION, 0),
    PhaseGate(PrebirthPhase.NEURAL_PLATE, 10),
    PhaseGate(PrebirthPhase.CORE_FORMATION, 25),
    PhaseGate(PrebirthPhase.LIMB_BUDS, 40),
    PhaseGate(PrebirthPhase.LIMB_EXTENSION, 60),
    PhaseGate(PrebirthPhase.PRE_BIRTH_STABLE, 80),
]


def phase_for_tick(tick: int) -> PrebirthPhase:
    current = PHASE_SCHEDULE[0].phase
    for gate in PHASE_SCHEDULE:
        if tick >= gate.min_ticks:
            current = gate.phase
    return current