# sandys_law_a7do/sandy_law/universal_mapping.py

def universal_signature(*, coherence: float, fragmentation: float) -> str:
    """
    Produces a small structural signature that is
    domain-independent.

    This is what makes Sandy’s Law universal.
    """

    def bin3(v: float) -> str:
        if v < 0.34:
            return "low"
        if v < 0.67:
            return "med"
        return "high"

    return f"c:{bin3(coherence)}|f:{bin3(fragmentation)}"
