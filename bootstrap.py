from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

# -------------------------
# Core systems
# -------------------------
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory
from scuttling.engine import ScuttlingEngine
from gates.engine import GateEngine

# -------------------------
# Genesis / birth
# -------------------------
from genesis.womb.physics import WombPhysicsEngine
from genesis.womb.umbilical import UmbilicalLink
from genesis.birth.criteria import BirthCriteria
from genesis.birth.transition import BirthTransitionEngine

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

# -------------------------
# Repetition
# -------------------------
from square.square import Square

# -------------------------
# World (NEW)
# -------------------------
from sandys_law_a7do.world.world_state import make_default_world
from sandys_law_a7do.world.runner import WorldRunner
from sandys_law_a7do.world.sensors import SensorSuite

# ============================================================
# SYSTEM CONSTRUCTOR
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:

    # -------------------------
    # WORLD (Phase 0)
    # -------------------------
    world = make_default_world()
    world_runner = WorldRunner(world)
    sensor_suite = SensorSuite(world)

    state: Dict[str, Any] = {
        # -----------------
        # Time
        # -----------------
        "ticks": 0,

        # -----------------
        # Core cognition
        # -----------------
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),
        "square": Square(),

        # -----------------
        # World
        # -----------------
        "world": world,
        "world_runner": world_runner,
        "sensor_suite": sensor_suite,

        # -----------------
        # Gestation
        # -----------------
        "womb_engine": WombPhysicsEngine(),
        "umbilical_link": UmbilicalLink(),

        # -----------------
        # Embodiment
        # -----------------
        "anatomy": create_default_anatomy(),
        "embodiment_growth": EmbodimentGrowthModel(),
        "embodiment_ledger": EmbodimentLedger(),

        # -----------------
        # Sensory
        # -----------------
        "sensory_readiness": SensoryReadiness(),
        "sensory_wall": SensoryWall(),
        "last_sensory_packets": [],

        # -----------------
        # Action scaffolding
        # -----------------
        "scuttling_engine": ScuttlingEngine(),

        # -----------------
        # Birth
        # -----------------
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # -----------------
        # Structural metrics
        # -----------------
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,

        # -----------------
        # Development trace
        # -----------------
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

        # -----------------
        # Cached states
        # -----------------
        "last_womb_state": None,
        "last_umbilical_state": None,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (OBSERVER SAFE)
# ============================================================

def system_snapshot(state: dict) -> dict:
    coherence = state["last_coherence"]
    load = state["structural_load"]

    world_snapshot = None
    if state.get("birth_state"):
        world_snapshot = state["world"].snapshot()

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Coherence": coherence,
            "Stability": coherence * (1.0 - load),
            "Load": load,
            "Z": state["last_fragmentation"],
        },
        "memory_count": state["memory"].count(),
        "gates": state["gate_engine"].snapshot().gates,
        "anatomy": anatomy_snapshot(state["anatomy"]),
        "sensory": state["sensory_readiness"].snapshot(),
        "square": state["square"].snapshot(),
        "world": world_snapshot,
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