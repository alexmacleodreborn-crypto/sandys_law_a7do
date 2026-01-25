# sandys_law_a7do/embodiment/thermal_pain.py

from dataclasses import dataclass


@dataclass(frozen=True)
class ThermalPain:
    """
    Represents thermal stress or damage.
    """
    intensity: float        # [0..1]
    sustained: bool
    source: str

    @property
    def harmful(self) -> bool:
        return self.intensity > 0.6 and self.sustained
