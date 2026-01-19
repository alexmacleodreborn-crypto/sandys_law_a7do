# sandys_law_a7do/education/exams.py

from dataclasses import dataclass
from typing import Dict


@dataclass
class Exam:
    """
    Defines an evaluation test.
    """
    name: str
    criteria: Dict[str, float]

    def evaluate(self, metrics: Dict[str, float]) -> "ExamResult":
        score = 0.0
        max_score = len(self.criteria)

        for key, threshold in self.criteria.items():
            if metrics.get(key, 0.0) >= threshold:
                score += 1.0

        return ExamResult(
            exam_name=self.name,
            score=score,
            max_score=max_score
        )


@dataclass
class ExamResult:
    exam_name: str
    score: float
    max_score: float

    @property
    def passed(self) -> bool:
        return self.score >= self.max_score
