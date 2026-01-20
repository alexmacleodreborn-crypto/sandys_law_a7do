# tests/test_embodiment.py

from embodiment.boundaries import BoundarySignal, BoundaryState
from embodiment.thermal_pain import ThermalPainSignal


def test_boundary_accumulation():
    state = BoundaryState()
    state.register(BoundarySignal("soft", 0.3, "near"))
    assert state.soft_pressure > 0.0


def test_thermal_pain_flag():
    pain = ThermalPainSignal(intensity=0.8, sustained=True, source="heat")
    assert pain.harmful is True
