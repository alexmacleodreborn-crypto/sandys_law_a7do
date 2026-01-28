"""
A7DO Bootstrap — Authoritative System Constructor

This file is the ONLY place where global system state is assembled.
"""

from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

# ============================================================
# Core systems
# ============================================================

from frames.store import FrameStore
from memory.structural_memory import StructuralMemory
from scuttling.engine import ScuttlingEngine
from gates.engine import GateEngine
from square.square import Square

# ============================================================
# Genesis / Birth
# ============================================================

from genesis.womb.physics import WombPhysicsEngine
from genesis.womb.umbilical import UmbilicalLink
from genesis.birth.criteria import BirthCriteria
from genesis.birth.transition import BirthTransitionEngine
from genesis.birth_state import BirthState

# ============================================================
# Embodiment
# ============================================================

from embodiment.anatomy import create_default_anatomy, anatomy_snapshot
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment
from embodiment.growth_model import EmbodimentGrowthModel

# ============================================================
# Sensory
# ============================================================

from sensory.readiness import SensoryReadiness
from sensory.wall import SensoryWall

# ============================================================
# World (Phase 0)
# ============================================================

from world.world_state import make_default_world
from world.world_runner import WorldRunner
from world.sensors import SensorSuite


# ============================================================
# SYSTEM CONSTRUCTOR
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    """
    Construct the full A7DO system.
    """

    # -------------------------
    # World (single instance)
    # -------------------------

    world = make_default_world()

    # -------------------------
    # Global mutable state
    # -------------------------

    state: Dict[str, Any] = {
        # Time
        "ticks": 0,

        # Core cognition
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),
        "square": Square(),

        # World
        "world": world,
        "world_runner": WorldRunner(world),
        "world_sensors": SensorSuite(world),

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

        # Birth
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # Structural metrics
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,

        # Observer-only development trace
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

        # Cached physics snapshots
        "last_womb_state": None,
        "last_umbilical_state": None,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (READ-ONLY, UI SAFE)
# ============================================================

def system_snapshot(state: dict) -> dict:
    coherence = float(state["last_coherence"])
    load = float(state["structural_load"])
    stability = coherence * (1.0 - load)

    # -------------------------
    # World snapshot
    # -------------------------

    world_snap = None
    ws = state.get("world")
    if ws:
        world_snap = {
            "cfg": {
                "width": ws.cfg.width,
                "height": ws.cfg.height,
                "move_cost": ws.cfg.move_cost,
                "block_cost": ws.cfg.block_cost,
                "contact_temp_gain": ws.cfg.contact_temp_gain,
                "pain_threshold": ws.cfg.pain_threshold,
            },
            "agent": {
                "x": ws.agent.x,
                "y": ws.agent.y,
                "effort": ws.agent.effort,
                "contact": ws.agent.contact,
                "thermal": ws.agent.thermal,
                "pain": ws.agent.pain,
            },
        }

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
            "Z": state["last_fragmentation"],
        },
        "world": world_snap,
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