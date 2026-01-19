# sandys_law_a7do/mind/coherence.py

from dataclasses import dataclass
from typing import Optional


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
    total_events: Optional[int] = None,
) -> CoherenceReport:
    """
    Compute coherence from simple structural proxies.

    No time, no reward, no semantics.
    """

    total = total_events if total_events is not None else max(1, fragment_count)

    # Fragmentation proxy
    frag = 0.0
    if fragment_count > 0:
        frag = min(1.0, unique_actions / fragment_count)

    # Coherence proxy = inverse fragmentation
    coh = max(0.0, 1.0 - frag)

    # Blocking proxy
    block_rate = min(1.0, blocked_events / max(1, total))

    return CoherenceReport(
        coherence=coh,
        fragmentation=frag,
        block_rate=block_rate,
    )
