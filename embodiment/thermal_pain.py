from __future__ import annotations
from dataclasses import dataclass


@dataclass(frozen=True)
class ThermalSignal:
    region: str
    temperature_delta: float


@dataclass(frozen=True)
class PainSignal:
    region: str
    intensity: float


class ThermalPainProcessor:
    """
    Converts raw physical exposure into bodily signals.
    """

    def thermal_to_signal(self, region: str, delta: float) -> ThermalSignal:
        return ThermalSignal(region=region, temperature_delta=delta)

    def pain_from_contact(self, region: str, force: float) -> PainSignal:
        intensity = min(1.0, force / 10.0)
        return PainSignal(region=region, intensity=intensity)
