"""
Embodiment Doctrine — Local Layer

This file is declarative only.
It documents invariants enforced by structure, not code.
"""

EMBODIMENT_PROPERTIES = {
    "persistent": True,
    "conditional": True,
    "local": True,
    "grounded": True,
}

PROHIBITED_BEHAVIOUR = [
    "symbolic reasoning",
    "belief storage",
    "instruction following",
    "external authority writes",
]

WRITE_PATH = [
    "closed_frames",
    "memory_patterns",
    "consolidation_gate",
    "embodiment_ledger",
]