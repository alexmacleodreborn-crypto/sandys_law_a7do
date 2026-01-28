from dataclasses import dataclass
from typing import Dict, List
import random
import time


# ============================================================
# Sensory Activation Event (NON-SEMANTIC)
# ============================================================

@dataclass(frozen=True)
class SensoryActivation:
    """
    A single degraded, body-localized sensory activation.
    """
    region: str
    modality: str
    intensity: float      # 0..1 (after attenuation)
    noise: float          # 0..1 (higher = less reliable)
    timestamp: float


# ============================================================
# Sensory Wall
# ============================================================

class SensoryWall:
    """
    Developmental sensory membrane.

    This class:
    - filters world stimuli into noise-dominated precursors
    - respects anatomy growth and sensory readiness
    - produces body-localized activations ONLY
    - NEVER produces meaning, symbols, or objects
    """

    def __init__(self) -> None:
        # Base noise floor for each modality
        self.base_noise = {
            "vision": 0.95,
            "auditory": 0.90,
            "touch": 0.70,
            "proprioception": 0.60,
            "balance": 0.80,
            "smell": 0.85,
            "taste": 0.85,
            "pain": 0.40,
        }

    # --------------------------------------------------------
    # Core filter
    # --------------------------------------------------------

    def filter(
        self,
        *,
        modality: str,
        raw_intensity: float,
        region: str,
        anatomy_growth: float,
        readiness: float,
    ) -> SensoryActivation | None:
        """
        Filter a raw world signal into a degraded sensory activation.

        Returns None if the anatomy or readiness is insufficient.
        """

        # --------------------------------------------------
        # HARD GATES (biology)
        # --------------------------------------------------

        if anatomy_growth < 0.25:
            return None

        if readiness <= 0.0:
            return None

        # --------------------------------------------------
        # Attenuation & noise
        # --------------------------------------------------

        # Overall gain depends on anatomy + readiness
        gain = anatomy_growth * readiness

        # Noise decays slowly with development
        base_noise = self.base_noise.get(modality, 0.9)
        noise = min(1.0, base_noise * (1.0 - 0.5 * readiness))

        # Final intensity is weak, noisy, and unreliable
        intensity = raw_intensity * gain
        intensity *= random.uniform(0.6, 1.0)

        # Clamp
        intensity = max(0.0, min(1.0, intensity))

        return SensoryActivation(
            region=region,
            modality=modality,
            intensity=intensity,
            noise=noise,
            timestamp=time.time(),
        )

    # --------------------------------------------------------
    # Batch helper (world tick)
    # --------------------------------------------------------

    def generate_activations(
        self,
        *,
        stimuli: List[Dict],
        anatomy: Dict[str, Dict],
        sensory_readiness: Dict[str, float],
    ) -> List[SensoryActivation]:
        """
        Convert a batch of world stimuli into sensory activations.
        """

        activations: List[SensoryActivation] = []

        for s in stimuli:
            region = s["region"]
            modality = s["modality"]

            anatomy_growth = anatomy.get(region, {}).get("growth", 0.0)
            readiness = sensory_readiness.get(modality, 0.0)

            act = self.filter(
                modality=modality,
                raw_intensity=s.get("intensity", 0.0),
                region=region,
                anatomy_growth=anatomy_growth,
                readiness=readiness,
            )

            if act is not None:
                activations.append(act)

        return activations