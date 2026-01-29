from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

from frames.store import FrameStore
from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.scuttling.engine import ScuttlingEngine
from sandys_law_a7do.gates.engine import GateEngine

from sandys_law_a7do.genesis.womb.physics import WombPhysicsEngine
from sandys_law_a7do.genesis.womb.umbilical import UmbilicalLink
from sandys_law_a7do.genesis.birth.criteria import BirthCriteria
from sandys_law_a7do.genesis.birth.transition import BirthTransitionEngine

from sandys_law_a7do.embodiment.anatomy import (
    create_default_anatomy,
    anatomy_snapshot,
)
from sandys_law_a7do.embodiment.ledger.ledger import EmbodimentLedger
from sandys_law_a7do.embodiment.bridge.accountant import summarize_embodiment
from sandys_law_a7do.embodiment.growth_model import EmbodimentGrowthModel

from sandys_law_a7do.sensory.readiness import SensoryReadiness
from sandys_law_a7do.sensory.wall import SensoryWall

from sandys_law_a7do.square.square import Square

from sandys_law_a7do.world.world_state import make_default_world
from sandys_law_a7do.world.runner import WorldRunner
from sandys_law_a7do.world.sensors import SensorSuite


def build_system() -> Tuple[Callable[[], dict], dict]:
    world = make_default_world()

    state: Dict[str, Any] = {
        "ticks": 0,

        # Core
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # World
        "world": world,
        "world_runner": WorldRunner(world),

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

        # Proto-cognition
        "square": Square(),

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

        # Observer trace
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
        "last_sensory_packets": [],
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


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
        "memory_count": state["memory"].count(),
        "gates": state["gate_engine"].snapshot().gates,
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
    }