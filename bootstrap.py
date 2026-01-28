"""
A7DO Bootstrap — Authoritative System Constructor

This file assembles ALL global system state.
If something doesn't move in Streamlit, it must be exposed here.
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
        # ------------------------------------------------
        # TIME
        # ------------------------------------------------
        "ticks": 0,

        # ------------------------------------------------
        # CORE
        # ------------------------------------------------
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # ------------------------------------------------
        # WOMB / GESTATION
        # ------------------------------------------------
        "womb_engine": WombPhysicsEngine(),
        "umbilical_link": UmbilicalLink(),

        # ------------------------------------------------
        # BIOLOGICAL EMBODIMENT
        # ------------------------------------------------
        "anatomy": create_default_anatomy(),
        "embodiment_growth": EmbodimentGrowthModel(),

        # ------------------------------------------------
        # SENSORY (POST-BIRTH)
        # ------------------------------------------------
        "sensory_readiness": SensoryReadiness(),
        "sensory_wall": SensoryWall(),
        "last_sensory_packets": [],

        # ------------------------------------------------
        # SCUTTLING (BODY SCHEMA)
        # ------------------------------------------------
        "scuttling_engine": ScuttlingEngine(),

        # ------------------------------------------------
        # BIRTH
        # ------------------------------------------------
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # ------------------------------------------------
        # STRUCTURAL METRICS
        # ------------------------------------------------
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,

        # ------------------------------------------------
        # DEVELOPMENT TRACE (OBSERVER ONLY)
        # ------------------------------------------------
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

        # ------------------------------------------------
        # LAST SNAPSHOTS (UI)
        # ------------------------------------------------
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
    frames = state["frames"]

    coherence = float(state["last_coherence"])
    load = float(state["structural_load"])
    stability = coherence * (1.0 - load)

    # -------------------------
    # Womb snapshot
    # -------------------------
    womb = None
    if state.get("last_womb_state"):
        ws = state["last_womb_state"]
        womb = {
            "tick": ws.tick,
            "heartbeat_rate": ws.heartbeat_rate,
            "ambient_load": ws.ambient_load,
            "rhythmic_stability": ws.rhythmic_stability,
            "womb_active": ws.womb_active,
        }

    # -------------------------
    # Umbilical snapshot
    # -------------------------
    umbilical = None
    if state.get("last_umbilical_state"):
        us = state["last_umbilical_state"]
        umbilical = {
            "active": us.active,
            "load_transfer": us.load_transfer,
            "rhythmic_coupling": us.rhythmic_coupling,
        }

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
            "Z": state["last_fragmentation"],
        },
        "womb": womb,
        "umbilical": umbilical,
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
        "active_frame": frames.active,
        "scuttling_candidates": state["scuttling_engine"].candidates_snapshot(),
    }