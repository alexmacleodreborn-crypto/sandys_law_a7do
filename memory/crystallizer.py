# sandys_law_a7do/memory/crystallizer.py
"""
Crystallizer — v1.1

Promotes buffered MemoryTrace objects into long-term StructuralMemory.

NOTE:
Clustering is intentionally NOT performed in v1.1.
This keeps memory semantics clean and avoids premature abstraction.
"""

from .structural_memory import StructuralMemory


def crystallize(memory: StructuralMemory) -> None:
    """
    Promote buffered traces into crystallised memory.
    """
    memory.crystallize()