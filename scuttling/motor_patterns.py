# sandys_law_a7do/scuttling/motor_patterns.py

from dataclasses import dataclass, field
from typing import List


@dataclass
class MotorPattern:
    """
    A repeatable movement sequence.
    """
    name: str
    sequence: List[str]
    load_cost: float          # [0..1]
    stability: float = 0.5    # [0..1]


@dataclass
class MotorPatternSet:
    """
    Collection of motor patterns.
    """
    patterns: List[MotorPattern] = field(default_factory=list)

    def viable(self, max_load: float) -> List[MotorPattern]:
        return [p for p in self.patterns if p.load_cost <= max_load]

    def most_stable(self) -> MotorPattern | None:
        if not self.patterns:
            return None
        return max(self.patterns, key=lambda p: p.stability)
