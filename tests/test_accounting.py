# tests/test_accounting.py

from accounting.metrics import (
    pressure_z,
    entropy_sigma,
    stability_index,
    coherence_index,
)


def test_pressure_z_basic():
    z = pressure_z(observed=1.0, expected=0.5)
    assert isinstance(z, float)


def test_entropy_non_negative():
    s = entropy_sigma(z_prev=1.0, z_curr=0.2)
    assert s >= 0.0


def test_stability_bounds():
    s = stability_index(0.0)
    assert 0.0 <= s <= 1.0


def test_coherence_series():
    c = coherence_index([0.1, 0.15, 0.2])
    assert 0.0 <= c <= 1.0
