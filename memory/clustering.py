# sandys_law_a7do/memory/clustering.py

from typing import List
from .trace import MemoryTrace
from .similarity import similarity_score


def cluster_traces(traces: List[MemoryTrace], threshold: float = 0.6):
    """
    Groups traces by structural similarity.
    Returns list of clusters (lists of traces).
    """
    clusters = []

    for trace in traces:
        placed = False
        for cluster in clusters:
            ref = cluster[0]
            score = similarity_score(trace.features, ref.features)
            if score >= threshold:
                cluster.append(trace)
                placed = True
                break

        if not placed:
            clusters.append([trace])

    return clusters
