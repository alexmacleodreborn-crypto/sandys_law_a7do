from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


# ============================================================
# Memory Doctrine
#
# - Memory is irreversible
# - Memory forms only from repeated stability
# - Memory cannot be written directly
# - Memory does not store meaning
# ============================================================


@dataclass(frozen=True)
class MemoryTrace:
    """
    A crystallized structural trace.

    This does NOT describe what something is.
    It only asserts that a pattern has stabilized.
    """
    signature: str
    strength: float
    frames_observed: int


@dataclass
class CrystallizerConfig:
    """
    Conservative thresholds.
    """
    min_strength: float = 0.75        # stability threshold
    min_frames: int = 6               # must repeat
    reinforcement: float = 0.08       # slow strengthening
    max_strength: float = 1.0


class MemoryCrystallizer:
    """
    Structural memory formation engine.

    Input:
      - PreferenceUpdate
      - AccountingEntry
    Output:
      - Optional MemoryTrace (only when crystallization occurs)
    """

    def __init__(self, cfg: Optional[CrystallizerConfig] = None) -> None:
        self.cfg = cfg or CrystallizerConfig()

        # Internal irreversible store
        self._traces: Dict[str, MemoryTrace] = {}

        # Observation counters
        self._counts: Dict[str, int] = {}

    # --------------------------------------------------------
    # Public API
    # --------------------------------------------------------

    def observe(
        self,
        *,
        context_key: str,
        preference_value: float,
    ) -> Optional[MemoryTrace]:
        """
        Observe a context preference.

        Memory forms ONLY if:
        - preference is high enough
        - context has been observed repeatedly
        """
        # Count observations
        self._counts[context_key] = self._counts.get(context_key, 0) + 1
        count = self._counts[context_key]

        # Below threshold → no memory
        if preference_value < self.cfg.min_strength:
            return None

        if count < self.cfg.min_frames:
            return None

        # Either create or reinforce trace
        if context_key in self._traces:
            old = self._traces[context_key]
            new_strength = min(
                self.cfg.max_strength,
                old.strength + self.cfg.reinforcement,
            )
            trace = MemoryTrace(
                signature=context_key,
                strength=new_strength,
                frames_observed=old.frames_observed + 1,
            )
        else:
            trace = MemoryTrace(
                signature=context_key,
                strength=preference_value,
                frames_observed=count,
            )

        # Irreversible write
        self._traces[context_key] = trace
        return trace

    # --------------------------------------------------------
    # Introspection (read-only)
    # --------------------------------------------------------

    def traces(self) -> List[MemoryTrace]:
        """
        Return all crystallized traces.
        """
        return list(self._traces.values())
