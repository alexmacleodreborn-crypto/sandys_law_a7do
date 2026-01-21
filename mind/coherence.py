# sandys_law_a7do/mind/coherence.py

from dataclasses import dataclass
from typing import Optional, List


@dataclass(frozen=True)
class CoherenceReport:
    """
    Structural coherence signal in [0..1].
    """
    coherence: float
    fragmentation: float
    block_rate: float


def compute_coherence(
    *,
    fragment_count: int,
    unique_actions: int,
    blocked_events: int = 0,
    percept_notes: Optional[List[str]] = None,
) -> CoherenceReport:
    """
    Compute coherence from structural + perceptual proxies.

    - No time
    - No reward
    - No semantics
    """

    total = max(1, fragment_count)

    # ---------------------------------
    # Fragmentation proxy
    # ---------------------------------
    fragmentation = min(1.0, unique_actions / total)

    # Base coherence (inverse fragmentation)
    coherence = max(0.0, 1.0 - fragmentation)

    # ---------------------------------
    # Perceptual modulation (NEW)
    # ---------------------------------
    if percept_notes:
        if "high_fragmentation" in percept_notes:
            coherence *= 0.75   # early warning drop

        if "repetitive" in percept_notes:
            coherence *= 0.90   # stagnation penalty

        if "empty" in percept_notes:
            coherence *= 1.05   # slight stability bias

    coherence = min(1.0, max(0.0, coherence))

    # ---------------------------------
    # Blocking proxy
    # ---------------------------------
    block_rate = min(1.0, blocked_events / total)

    return CoherenceReport(
        coherence=coherence,
        fragmentation=fragmentation,
        block_rate=block_rate,
    )