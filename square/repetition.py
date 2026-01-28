from collections import defaultdict
from dataclasses import dataclass

@dataclass
class RepetitionRecord:
    count: int = 0
    stability: float = 0.0


class RepetitionTracker:
    """
    Tracks repeated sensory patterns over time.
    """

    def __init__(self):
        self.records = defaultdict(RepetitionRecord)

    def observe(self, key: str):
        rec = self.records[key]
        rec.count += 1
        rec.stability = min(1.0, rec.stability + 0.1)

    def snapshot(self):
        return {
            k: {"count": v.count, "stability": round(v.stability, 3)}
            for k, v in self.records.items()
            if v.count > 1
        }