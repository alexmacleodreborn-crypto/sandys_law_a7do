# sandys_law_a7do/sandy_law/coherence_law.py

def coherence_value(*, fragments: int, unique: int) -> float:
    """
    Law-level coherence.

    Coherence increases when structure repeats.
    Returns value in [0..1].
    """
    if fragments <= 0:
        return 0.0

    ratio = unique / fragments
    return max(0.0, 1.0 - ratio)


def fragmentation_value(*, fragments: int, unique: int) -> float:
    """
    Law-level fragmentation.
    Returns value in [0..1].
    """
    if fragments <= 0:
        return 0.0

    return min(1.0, unique / fragments)
