# sandys_law_a7do/frames/frame.py

from dataclasses import dataclass, field
from typing import List
from .fragment import Fragment

@dataclass
class Frame:
    domain: str
    label: str
    fragments: List[Fragment] = field(default_factory=list)

    def add(self, fragment: Fragment):
        self.fragments.append(fragment)

