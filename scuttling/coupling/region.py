# sandys_law_a7do/scuttling/coupling/region.py

from dataclasses import dataclass

@dataclass
class BodyRegion:
    """
    Structural body region.

    No behavior.
    No control.
    Just physical presence.
    """
    name: str
    load: float = 0.0        # [0..1]
    stability: float = 0.5   # [0..1]