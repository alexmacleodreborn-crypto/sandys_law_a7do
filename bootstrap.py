"""
A7DO Bootstrap — Authoritative System Constructor

Responsibilities:
- Construct system state
- Own time progression
- Expose snapshot() for UI
- Coordinate prebirth, scuttling, embodiment, cognition
"""

from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

# -------------------------
# Core systems
# -------------------------
from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.gates.engine import GateEngine

# -------------------------
# Genesis / embodiment
# -------------------------
from sandys_law_a7do.scuttling.engine import ScuttlingEngine
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator

from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment


# ============================================================
# SYSTEM CONSTRUCTOR
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    """
    Construct the full A7DO system.

    Returns:
        snapshot() -> dict
        state -> mutable system state
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
        # Prebirth & embodiment
        # -----------------
        "womb_engine": WombPhysicsEngine(),
        "scuttling_engine": ScuttlingEngine(),
        "embodiment_ledger": EmbodimentLedger(),

        # -----------------
        # Birth
        # -----------------
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # -----------------
        # Structural channels (written by tick)
        # -----------------
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,
        "prediction_error": 0.0,

        # -----------------
        # Cached views
        # -----------------
        "last_womb_state": None,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (READ-ONLY)
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames = state["frames"]

    coherence = float(state.get("last_coherence", 0.0))
    Z = float(state.get("last_fragmentation", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # Gates
    gates = {}
    ge = state.get("gate_engine")
    if ge:
        try:
            snap = ge.snapshot()
            for name, g in (snap.get("gates") or {}).items():
                gates[name] = {
                    "state": getattr(g, "state", None),
                    "open": getattr(g, "open", None),
                    "reason": getattr(g, "reason", None),
                    "last_tick": getattr(g, "last_tick", None),
                }
        except Exception:
            pass

    # Embodiment summary
    embodiment = None
    try:
        embodiment = summarize_embodiment(state["embodiment_ledger"])
    except Exception:
        pass

    # Womb
    womb = None
    ws = state.get("last_womb_state")
    if ws:
        womb = {
            "heartbeat_rate": ws.heartbeat_rate,
            "ambient_load": ws.ambient_load,
            "rhythmic_stability": ws.rhythmic_stability,
            "womb_active": ws.womb_active,
        }

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
        },
        "active_frame": frames.active,
        "memory_count": state["memory"].count(),
        "prediction_error": state.get("prediction_error", 0.0),
        "gates": gates,
        "embodiment": embodiment,
        "womb": womb,
        "birth": (
            {
                "born": state["birth_state"].born,
                "reason": state["birth_state"].reason,
                "tick": state["birth_state"].tick,
            }
            if state.get("birth_state")
            else None
        ),
        "scuttling_candidates": state["scuttling_engine"].candidates_snapshot(),
    }