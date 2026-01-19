# sandys_law_a7do/education/cv.py

from dataclasses import dataclass, field
from typing import List
from .exams import ExamResult


@dataclass
class CurriculumVitae:
    """
    Records completed exams and milestones.
    """
    exams: List[ExamResult] = field(default_factory=list)

    def record(self, result: ExamResult):
        self.exams.append(result)

    def passed_exams(self) -> List[str]:
        return [e.exam_name for e in self.exams if e.passed]

    def summary(self) -> dict:
        return {
            "total_exams": len(self.exams),
            "passed": len(self.passed_exams())
        }
