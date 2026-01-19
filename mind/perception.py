# sandys_law_a7do/mind/perception.py

from dataclasses import dataclass
from typing import Dict, Any, List


@dataclass(frozen=True)
class PerceptSummary:
    """
    Structural summary of a frame or interaction batch.
    """
    fragment_count: int
    unique_actions: int
    notes: List[str]


def summarize_perception(fragments: List[Dict[str, Any]]) -> PerceptSummary:
    """
    Convert raw fragments/events into a compact percept.

    fragments: list of dicts with at least an 'action' key
    """
    actions = [f.get("action") for f in fragments if "action" in f]
    fragment_count = len(actions)
    unique_actions = len(set(actions))

    notes: List[str] = []

    if fragment_count == 0:
        notes.append("empty")

    if unique_actions > fragment_count * 0.6:
        notes.append("high_fragmentation")

    if fragment_count >= 5 and unique_actions <= 2:
        notes.append("repetitive")

    return PerceptSummary(
        fragment_count=fragment_count,
        unique_actions=unique_actions,
        notes=notes,
    )
