# sandys_law_a7do/scuttling/motor_patterns.py

from dataclasses import dataclass, field
from typing import List
import random


@dataclass
class MotorPattern:
    """
    A repeatable impulsive movement pattern.
    This is PRE-INTENT and PRE-AWARENESS.
    """
    name: str
    sequence: List[str]

    # Structural properties
    load_cost: float          # [0..1]
    stability: float = 0.2    # [0..1] newborn-level default

    # Developmental bookkeeping
    exposures: int = 0        # how many times this fired


    def reinforce(self, growth_rate: float) -> None:
        """
        Reinforce pattern stability through repetition.
        """
        self.exposures += 1
        self.stability += growth_rate * (1.0 - self.stability)
        self.stability = min(1.0, self.stability)


    def decay(self, load: float) -> None:
        """
        High load destabilizes motor patterns.
        """
        penalty = load * self.load_cost * 0.1
        self.stability -= penalty
        self.stability = max(0.0, self.stability)


@dataclass
class MotorPatternSet:
    """
    Collection of impulsive motor patterns.

    This set DOES NOT choose.
    It is exposed to impulses during growth epochs.
    """
    patterns: List[MotorPattern] = field(default_factory=list)


    def impulse_fire(self, impulse_rate: float) -> List[MotorPattern]:
        """
        Randomly fire motor patterns during growth.
        Returns patterns that were activated this epoch.
        """
        fired: List[MotorPattern] = []

        for p in self.patterns:
            if random.random() < impulse_rate:
                fired.append(p)

        return fired


    def growth_epoch_update(
        self,
        *,
        growth_rate: float,
        structural_load: float,
        impulse_rate: float,
    ) -> None:
        """
        One developmental growth epoch.

        - Impulses fire blindly
        - Fired patterns reinforce
        - Load applies decay
        """

        fired = self.impulse_fire(impulse_rate)

        for p in self.patterns:
            if p in fired:
                p.reinforce(growth_rate)
            p.decay(structural_load)


    def most_stable(self) -> MotorPattern | None:
        """
        Introspection helper (READ-ONLY).
        """
        if not self.patterns:
            return None
        return max(self.patterns, key=lambda p: p.stability)