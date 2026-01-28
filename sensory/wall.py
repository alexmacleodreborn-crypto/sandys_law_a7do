from dataclasses import dataclass
from typing import Dict, List


# ============================================================
# PRE-SEMANTIC SENSORY PACKET
# ============================================================

@dataclass(frozen=True)
class SensoryPacket:
    """
    A degraded, body-localized sensory activation.

    This is NOT perception.
    This is NOT meaning.
    This is a physiological precursor only.
    """
    modality: str           # vision, sound, touch, smell, taste
    body_region: str        # eye, ear, skin, nose, mouth
    intensity: float        # 0..1 (weak, noisy)
    coherence: float        # 0..1 (structure, not meaning)
    repetition: float       # 0..1 (temporal recurrence)


# ============================================================
# SENSORY WALL
# ============================================================

class SensoryWall:
    """
    Developmental sensory membrane.

    Converts raw world stimulus into
    noisy, body-bound, pre-semantic packets.
    """

    def __init__(self) -> None:
        self._history: Dict[str, float] = {}

    # --------------------------------------------------------
    # MAIN FILTER
    # --------------------------------------------------------

    def filter(
        self,
        *,
        raw_input: Dict[str, float],
        anatomy: Dict[str, Dict[str, float]],
        sensory_levels: Dict[str, float],
    ) -> List[SensoryPacket]:

        packets: List[SensoryPacket] = []

        for modality, raw_intensity in raw_input.items():
            readiness = sensory_levels.get(modality, 0.0)
            if readiness <= 0.0:
                continue

            body_region = self._map_modality_to_body(modality)
            if body_region not in anatomy:
                continue

            growth = anatomy[body_region]["growth"]
            if growth < 0.3:
                continue  # organ not mature enough

            key = f"{modality}:{body_region}"
            prev_rep = self._history.get(key, 0.0)
            repetition = min(1.0, prev_rep + 0.08)

            coherence = min(
                1.0,
                readiness * growth * repetition,
            )

            intensity = raw_intensity * readiness * growth

            packets.append(
                SensoryPacket(
                    modality=modality,
                    body_region=body_region,
                    intensity=round(intensity, 3),
                    coherence=round(coherence, 3),
                    repetition=round(repetition, 3),
                )
            )

            self._history[key] = repetition

        return packets

    # --------------------------------------------------------
    # MODALITY → BODY MAP
    # --------------------------------------------------------

    @staticmethod
    def _map_modality_to_body(modality: str) -> str:
        return {
            "vision": "eyes",
            "sound": "ears",
            "touch": "skin",
            "smell": "nose",
            "taste": "mouth",
            "balance": "spine",
        }.get(modality, "")