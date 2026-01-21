"""
Bootstrap — v1.2 (STABLE)

Responsibilities:
- Owns all system state
- Enforces structural order (Frame → Fragment → Tick)
- No UI logic
"""

# =====================================================
# CORE STRUCTURES
# =====================================================

from .frames.store import FrameStore
from .frames.frame import Frame
from .frames.fragment import Fragment

from .mind.coherence import compute_coherence
from .mind.regulation import regulate

from .memory.trace import MemoryTrace
from .memory.structural_memory import StructuralMemory
from .memory.crystallizer import crystallize
from .memory.decay import decay_weight


# =====================================================
# FROZEN REGULATION THRESHOLDS
# =====================================================

Z_MAX = 0.6
COHERENCE_MIN = 0.7
STABILITY_MIN = 0.7
MEMORY_PERSIST_TICKS = 3


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,
        "stable_ticks": 0,
        "metric_history": {
            "ticks": [],
            "Z": [],
            "Coherence": [],
            "Stability": [],
        },
        "crystallisation_ticks