# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.7 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- Episode commit on frame close (Option A)
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)
- Structural load & stability divergence (Phase 5)
- Preference drift update on episode close (Phase 6)
- Gate visibility (Phase 7.3) — READ ONLY

MemoryTrace signature (AUTHORITATIVE):
MemoryTrace(
    tick,
    Z,
    coherence,
    stability,
    frame_signature,
    weight=1.0,
    tags=[...]
)
"""

# =====================================================
# CORE STRUCTURE
# =====================================================

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.perception import summarize_perception

from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory

from sandys_law_a7do.integration.perception_loop import perceive_and_act

# Phase 7.3 — Gates (READ ONLY)
from sandys_law_a7do.gates.engine import GateEngine


# =====================================================
# SYSTEM BUILD
# =====================================================

def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(store=pref_store, cfg=PreferenceConfig())

    gate_engine = GateEngine()

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # Phase