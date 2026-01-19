from __future__ import annotations
import math
from typing import Dict, List, Tuple

from sandys_law_a7do.frames.fragment import Fragment

EPS = 1e-12

def kind_distribution(frags: List[Fragment]) -> Dict[str, float]:
    if not frags:
        return {}
    counts: Dict[str, int] = {}
    for f in frags:
        counts[f.kind] = counts.get(f.kind, 0) + 1
    n = float(len(frags))
    return {k: c / n for k, c in counts.items()}

def normalized_entropy(p: Dict[str, float]) -> float:
    if not p:
        return 1.0
    K = max(1, len(p))
    H = 0.0
    for v in p.values():
        H -= float(v) * math.log(float(v) + EPS)
    return float(H / math.log(K + EPS))

def coherence_fragmentation(frags: List[Fragment]) -> Tuple[float, float]:
    p = kind_distribution(frags)
    Hn = normalized_entropy(p)
    C = 1.0 - Hn
    Phi = Hn
    return (float(C), float(Phi))

def embodiment_load(frags: List[Fragment]) -> float:
    # conservative: load comes from thermal/pain fields if present
    load = 0.0
    for f in frags:
        if f.kind == "thermal":
            load += abs(float(f.payload.get("delta", 0.0)))
        if f.kind == "pain":
            load += abs(float(f.payload.get("level", 0.0)))
    return float(max(0.0, min(1.0, load)))
