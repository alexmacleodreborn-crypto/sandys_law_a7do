# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (Streamlit-safe)
"""

# =========================================================
# CORE IMPORTS ONLY (NO UI)
# =========================================================

from roles.system_manager import SystemManager
from roles.sled_interface import SLEDInterface

from frames.store import FrameStore
from memory.structural_memory import StructuralMemory

from embodiment.ledger import EmbodimentLedger
from embodiment.boundaries import BoundaryState

from mind.preference import PreferenceEngine
from mind.perception import summarize_perception
from mind.coherence import compute_coherence
from mind.regulation import regulate

from accounting.metrics import metric_bundle


# =========================================================
# SYSTEM CONSTRUCTION
# =========================================================

def build_system():
    """
    Construct and wire the full system.
    Returns (system_manager, snapshot_provider)
    """

    frames = FrameStore()
    memory = StructuralMemory()

    embodiment_ledger = EmbodimentLedger()
    boundaries = BoundaryState()

    preferences = PreferenceEngine()

    system = SystemManager()
    sled = SLEDInterface()
    system.register(sled)

    def snapshot():
        active_frames = frames.frames if hasattr(frames, "frames") else []

        fragments = []
        for f in active_frames:
            for frag in getattr(f, "fragments", []):
                fragments.append({"action": getattr(frag, "kind", "unknown")})

        percept = summarize_perception(fragments)

        hard_pressure = getattr(boundaries, "hard_pressure", 0.0)
        blocked_events = int(hard_pressure * 10)

        coherence = compute_coherence(
            fragment_count=percept.fragment_count,
            unique_actions=percept.unique_actions,
            blocked_events=blocked_events,
        )

        regulation = regulate(
            coherence=coherence.coherence,
            fragmentation=coherence.fragmentation,
            block_rate=coherence.block_rate,
        )

        metrics = metric_bundle(
            {
                "Z": coherence.fragmentation,
                "Sigma": coherence.coherence,
                "Stability": 1.0 - coherence.fragmentation,
                "Coherence": coherence.coherence,
            }
        )

        return {
            "roles": list(system.roles.keys()),
            "frames": active_frames,
            "metrics": metrics,
            "regulation": {
                "decision": regulation.decision,
                "reason": regulation.reason,
            },
        }

    return system, snapshot