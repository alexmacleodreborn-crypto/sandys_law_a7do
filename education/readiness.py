# sandys_law_a7do/education/readiness.py

from typing import Dict


def readiness_score(metrics: Dict[str, float]) -> float:
    """
    Computes overall readiness based on coherence and stability.
    """
    stability = metrics.get("Stability", 0.0)
    coherence = metrics.get("Coherence", 0.0)

    return 0.5 * stability + 0.5 * coherence
