from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class Frame:
    """
    Developmental frame.

    A frame represents a bounded window of growth.
    It contains PHASES, not fragments.
    """

    domain: str
    label: str

    # Developmental phases occurring in this frame
    phases: List[Dict[str, Any]] = field(default_factory=list)

    def add_phase(self, phase: Dict[str, Any]) -> None:
        """
        Add a developmental phase marker.

        Phase examples:
        - prebirth_growth
        - limb_formation
        - neural_rhythm
        """
        self.phases.append(phase)