from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class RegionLedger:
    contacts: int = 0
    pain_events: int = 0
    thermal_load: float = 0.0
    effort: float = 0.0


class EmbodimentLedger:
    """
    Persistent bodily history.
    """

    def __init__(self) -> None:
        self._regions: Dict[str, RegionLedger] = {}

    def _ensure(self, region: str) -> None:
        if region not in self._regions:
            self._regions[region] = RegionLedger()

    def record_contact(self, region: str) -> None:
        self._ensure(region)
        self._regions[region].contacts += 1

    def record_pain(self, region: str) -> None:
        self._ensure(region)
        self._regions[region].pain_events += 1

    def record_thermal(self, region: str, value: float) -> None:
        self._ensure(region)
        self._regions[region].thermal_load += value

    def record_effort(self, region: str, effort: float) -> None:
        self._ensure(region)
        self._regions[region].effort += effort

    def snapshot(self) -> Dict[str, RegionLedger]:
        return self._regions.copy()
