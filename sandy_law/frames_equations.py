# sandys_law_a7do/sandy_law/frames_equations.py

def frame_pressure(*, expected: int, observed: int) -> float:
    """
    Frame pressure Z.

    Pressure arises from deviation from expectation.
    Normalised to [0..1].
    """
    if expected <= 0:
        return 0.0

    delta = abs(observed - expected)
    return min(1.0, delta / expected)


def frame_entropy(*, pressure_prev: float, pressure_curr: float) -> float:
    """
    Entropy release Σ when pressure drops.
    """
    if pressure_curr < pressure_prev:
        return pressure_prev - pressure_curr
    return 0.0
