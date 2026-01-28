"""
A7DO Bootstrap — Authoritative System Constructor

This file is the ONLY place where global system state is assembled.
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


# ============================================================
# SYSTEM CONSTRUCTOR
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    """
    Construct the full A7DO system.
    """

    state: Dict[str, Any] = {
        # -----------------
        # Time
        # -----------------
        "ticks": 0,

        # -----------------
        # Core runtime
        # -----------------
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # -----------------
        # Womb & gestation
        # -----------------
        "womb_engine": WombPhysicsEngine(),
        "umbilical_link": UmbilicalLink(),

        # -----------------
        # Embodiment (BIOLOGICAL)
        # -----------------
        "anatomy": create_default_anatomy(),
        "embodiment_growth": EmbodimentGrowthModel(),
        "embodiment_ledger": EmbodimentLedger(),

        # -----------------
        # Scuttling (POST-BIRTH)
        # -----------------
        "scuttling_engine": ScuttlingEngine(),

        # -----------------
        # Sensory (POST-BIRTH)
        # -----------------
        "sensory_readiness": SensoryReadiness(),

        # -----------------
        # Birth (authoritative)
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
        # Development trace (observer only)
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
        # Cached snapshots
        # -----------------
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

    coherence = float(state.get("last_coherence", 0.0))
    fragmentation = float(state.get("last_fragmentation", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # Gates
    gates = {}
    ge = state.get("gate_engine")
    if ge:
        try:
            snap = ge.snapshot()
            for name, g in snap.gates.items():
                gates[name] = g
        except Exception:
            pass

    # Embodiment summary
    embodiment = None
    try:
        embodiment = summarize_embodiment(state["embodiment_ledger"])
    except Exception:
        pass

    # Womb snapshot
    womb = None
    ws = state.get("last_womb_state")
    if ws:
        womb = {
            "heartbeat_rate": ws.heartbeat_rate,
            "ambient_load": ws.ambient_load,
            "rhythmic_stability": ws.rhythmic_stability,
            "womb_active": ws.womb_active,
        }

    # Umbilical snapshot
    umbilical = None
    us = state.get("last_umbilical_state")
    if us:
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
            "Z": fragmentation,
        },
        "active_frame": frames.active,
        "memory_count": state["memory"].count(),
        "gates": gates,
        "anatomy": anatomy_snapshot(state["anatomy"]),
        "embodiment": embodiment,
        "womb": womb,
        "umbilical": umbilical,
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