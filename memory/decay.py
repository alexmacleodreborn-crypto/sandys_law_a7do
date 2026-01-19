# sandys_law_a7do/memory/decay.py

def decay_weight(rate: float) -> float:
    """
    Returns a decay multiplier.
    Rate must be in (0,1].
    """
    if rate <= 0:
        return 1.0
    if rate >= 1:
        return 0.0
    return 1.0 - rate
