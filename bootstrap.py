from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

# ---------------------------------------------
# Core
# ---------------------------------------------
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory
from gates.engine import GateEngine

# ---------------------------------------------
# Genesis
# ---------------------------------------------
from genesis.womb.physics import WombPhysicsEngine
from genesis.womb.umbilical import UmbilicalLink
from genesis.birth.criteria import BirthCriteria
from genesis.birth.transition import BirthTransitionEngine

# ---------------------------------------------
# Embodiment
# ---------------------------------------------
from embodiment.anatomy import create_default_anatomy, anatomy_snapshot
from embodiment.growth_model import EmbodimentGrowthModel
from embodiment.ledger.ledger import EmbodimentLedger

# ---------------------------------------------
# Sensory / proto-cognition
# ---------------------------------------------
from sensory.readiness import SensoryReadiness
from sensory.wall import SensoryWall
from square.square import Square

# ---------------------------------------------
# Scuttling
# ---------------------------------------------
from scuttling.engine import ScuttlingEngine

# ---------------------------------------------
# WORLD (NEW — REQUIRED)
# ---------------------------------------------
from world.world_state import make_default_world
from world.world_runner import WorldRunner
from world.sensors import SensorSuite


# =================================================
# SYSTEM CONSTRUCTOR
# =================================================

def build_system() -> Tuple[Callable[[], dict], dict]:

    world = make_default_world()

    state: Dict[str, Any] = {

        # Time
        "ticks": 0,

        # Core
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # Genesis
        "womb_engine": WombPhysicsEngine(),
        "umbilical_link": UmbilicalLink(),

        # Embodiment
        "anatomy": create_default_anatomy(),
        "embodiment_growth": EmbodimentGrowthModel(),
        "embodiment_ledger": EmbodimentLedger(),

        # Sensory
        "sensory_readiness": SensoryReadiness(),
        "sensory_wall": SensoryWall(),
        "square": Square(),

        # Scuttling
        "scuttling_engine": ScuttlingEngine(),

        # Birth
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # World (ALWAYS PRESENT)
        "world": world,
        "world_runner": WorldRunner(world),
        "sensor_suite": SensorSuite(world),

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

        # Cached
        "last_womb_state": None,
        "last_umbilical_state": None,
        "last_sensory_packets": [],
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# =================================================
# SNAPSHOT
# =================================================

def system_snapshot(state: dict) -> dict:

    coherence = state["last_coherence"]
    load = state["structural_load"]

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Coherence": coherence,
            "Stability": coherence * (1.0 - load),
            "Load": load,
            "Z": state["last_fragmentation"],
        },
        "anatomy": anatomy_snapshot(state["anatomy"]),
        "sensory": state["sensory_readiness"].snapshot(),
        "square": state["square"].snapshot(),
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
        "world": state["world"].snapshot(),
    }