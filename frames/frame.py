from dataclasses import dataclass, field
from typing import List
from .fragment import Fragment


@dataclass
class Frame:
    """
    Structural frame container.

    Frames:
    - hold structural signals (phase, perception, contact, etc.)
    - are NOT semantic
    - do NOT imply learning or intention
    """

    domain: str
    label: str
    fragments: List[Fragment] = field(default_factory=list)

    def add(self, fragment: Fragment) -> None:
        self.fragments.append(fragment)