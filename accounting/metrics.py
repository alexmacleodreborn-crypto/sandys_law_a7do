# sandys_law_a7do/accounting/metrics.py

"""
Metrics module

Pure metric functions.
NO state.
NO memory.
NO learning.
NO UI.

This module only measures.
Interpretation belongs elsewhere.
"""

from typing import Dict


# =====================================================
# CORE METRICS
# =====================================================

def pressure_z(observed: float, expected: float) -> float:
    """
    Z = deviation from expectation.
    """
    return observed - expected


def entropy_sigma(z_prev: float, z_curr: float, gain: float = 0.5) -> float:
    """
    Σ = entropy release when surprise is reduced.
    """
    if abs(z_curr) < abs(z_prev):
        return gain * (abs(z_prev) - abs(z_curr))
    return 0.0


def relax_pressure(z: float, sigma: float, cap: float = 0.8) -> float:
    """
    Pressure relaxation due to entropy.
    """
    return z * (1.0 - min(sigma, cap))


# =====================================================
# STABILITY & COHERENCE
# =====================================================

def stability_index(z: float, tolerance: float = 0.1) -> float:
    """
    Measures how close the system is to equilibrium.
    1.0 = perfectly stable
    """
    return max(0.0, 1.0 - abs(z) / tolerance)


def coherence_index(z_series: list[float]) -> float:
    """
    Measures smoothness of pressure evolution.
    """
    if len(z_series) < 2:
        return 1.0

    diffs = [abs(z_series[i] - z_series[i - 1]) for i in range(1, len(z_series))]
    avg_diff = sum(diffs) / len(diffs)

    return 1.0 / (1.0 + avg_diff)


# =====================================================
# AGGREGATION
# =====================================================

def metric_bundle(values: Dict[str, float]) -> Dict[str, float]:
    """
    Standard metric packaging.
    """
    return {
        "Z": values.get("Z", 0.0),
        "Sigma": values.get("Sigma", 0.0),
        "Stability": values.get("Stability", 0.0),
        "Coherence": values.get("Coherence", 0.0),
    }
