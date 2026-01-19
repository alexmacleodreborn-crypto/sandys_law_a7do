from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class MemoryTrace:
    signature: str
    strength: float
    frames_observed: int
    signatures: List[str] = field(default_factory=list)

    # --------------------------------------------------------

    @classmethod
    def from_frames(
        cls,
        *,
        frames: List,
        coherence: float,
        fragmentation: float,
    ) -> "MemoryTrace":
        sigs = []
        for f in frames:
            for frag in f.fragments:
                sigs.append(f"{frag.kind}:{frag.payload.get('region','*')}")

        signature = "|".join(sorted(set(sigs)))
        strength = max(0.0, coherence - fragmentation)

        return cls(
            signature=signature,
            strength=strength,
            frames_observed=1,
            signatures=list(set(sigs)),
        )

    # --------------------------------------------------------

    def merge(self, other: "MemoryTrace") -> None:
        self.frames_observed += other.frames_observed
        self.strength = min(
            1.0,
            (self.strength + other.strength) / 2.0,
        )
