# sandys_law_a7do/education/curriculum.py

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class Curriculum:
    """
    Defines an ordered set of learning domains or challenges.
    """
    name: str
    stages: List[str] = field(default_factory=list)
    requirements: Dict[str, float] = field(default_factory=dict)

    def add_stage(self, stage: str):
        if stage not in self.stages:
            self.stages.append(stage)

    def set_requirement(self, metric: str, threshold: float):
        self.requirements[metric] = threshold

    def is_stage_allowed(self, metrics: Dict[str, float]) -> bool:
        """
        Checks whether current metrics satisfy curriculum requirements.
        """
        for key, threshold in self.requirements.items():
            if metrics.get(key, 0.0) < threshold:
                return False
        return True
