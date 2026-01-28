"""
A7DO Bootstrap — Authoritative System Constructor
"""

from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

# -------------------------
# Core systems
# -------------------------
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory
from scuttling.engine import ScuttlingEngine

# -------------------------
# Gates
# -------------------------
from gates.engine import GateEngine

# -------------------------
# Genesis / birth
# -------------------------
from genesis.womb.physics import WombPhysicsEngine
from genesis.womb.umbilical import UmbilicalLink
from genesis.birth.criteria import BirthCriteria
from genesis.birth.transition import BirthTransitionEngine
from genesis.birth_state import BirthState

# -------------------------
# Embodiment
# -------------------------
from embodiment.anatomy import create_default_anatomy, anatomy_snapshot
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment
from embodiment.growth_model import EmbodimentGrowthModel

# -------------------------
# Sensory
# -------------------------
from sensory.readiness import SensoryReadiness
from sensory.wall import SensoryWall


# ============================================================
# SYSTEM CONSTRUCTOR
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:

    state: Dict[str, Any] = {
        "ticks": 0,

        # Core
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # Gestation
        "womb_engine": WombPhysicsEngine(),
        "umbilical_link": UmbilicalLink(),

        # Embodiment
        "anatomy": create_default_anatomy(),
        "embodiment_growth": EmbodimentGrowthModel(),
        "embodiment_ledger": EmbodimentLedger(),

        # Sensory
        "sensory_readiness": SensoryReadiness(),
        "sensory_wall": SensoryWall(),
        "last_sensory_packets": [],

        # Scuttling
        "scuttling_engine": ScuttlingEngine(),

        # Birth
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # Metrics
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,

        # Trace
        "development_trace": {
            "ticks": [],
            "heartbeat": [],
            "ambient_load": [],
            "stability": [],
            "brain_coherence": [],
            "body_growth": [],
            "limb_growth": [],
            "umbilical_load": [],
            "rhythmic_coupling": [],
        },

        "last_womb_state": None,
        "last_umbilical_state": None,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames = state["frames"]

    coherence = float(state["last_coherence"])
    load = float(state["structural_load"])
    stability = coherence * (1.0 - load)

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
            "Z": state["last_fragmentation"],
        },
        "active_frame": frames.active,
        "memory_count": state["memory"].count(),
        "gates": state["gate_engine"].snapshot().gates,
        "anatomy": anatomy_snapshot(state["anatomy"]),
        "sensory": state["sensory_readiness"].snapshot(),
        "birth": (
            {
                "born": state["birth_state"].born,
                "reason": state["birth_state"].reason,
                "tick": state["birth_state"].tick,
            }
            if state["birth_state"]
            else None
        ),
        "scuttling_candidates": state["scuttling_engine"].candidates_snapshot(),
    }