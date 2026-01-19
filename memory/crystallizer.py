# sandys_law_a7do/memory/crystallizer.py

from typing import List, Dict
from .trace import MemoryTrace


def crystallize(cluster: List[MemoryTrace]) -> Dict:
    """
    Converts a cluster into a structural memory pattern.
    """
    if not cluster:
        return {}

    pattern = {}
    for trace in cluster:
        for k, v in trace.features.items():
            pattern.setdefault(k, set()).add(v)

    return {
        "pattern": {k: list(v) for k, v in pattern.items()},
        "strength": sum(t.weight for t in cluster),
        "size": len(cluster)
    }
