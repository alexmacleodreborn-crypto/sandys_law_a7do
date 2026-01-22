# sandys_law_a7do/embodiment/local/copilot/buffer.py
"""
Local Copilot Buffer — Phase A4.1 (LOCKED)

Stores:
- Procedural local responses
- Stability-weighted patterns
- NO semantics
- NO symbols
- NO rewards
"""

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class CopilotBuffer:
    """
    Local procedural memory for a single region.
    """
    patterns: Dict[str, float] = field(default_factory=dict)
    total_exposures: int = 0

    def reinforce(self, pattern: str, stability: float) -> None:
        """
        Reinforce a procedural pattern.
        """
        self.total_exposures += 1
        prev = self.patterns.get(pattern, 0.0)
        self.patterns[pattern] = min(1.0, prev + stability * 0.1)

    def best_pattern(self) -> str | None:
        if not self.patterns:
            return None
        return max(self.patterns, key=self.patterns.get)