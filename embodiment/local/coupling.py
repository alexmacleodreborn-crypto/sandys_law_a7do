# embodiment/local/coupling.py

from dataclasses import dataclass
from typing import Dict, Set


@dataclass
class RegionCoupling:
    """
    Defines mechanical influence between regions.
    """
    neighbors: Dict[str, Set[str]]

    def coupled(self, region: str) -> Set[str]:
        return self.neighbors.get(region, set())

    def propagate_load(self, region: str, load: float) -> Dict[str, float]:
        """
        Distribute load to coupled regions.
        """
        affected = self.coupled(region)
        if not affected:
            return {}

        share = load / len(affected)
        return {r: share for r in affected}