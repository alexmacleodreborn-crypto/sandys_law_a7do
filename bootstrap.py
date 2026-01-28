"""
A7DO Bootstrap — Authoritative System Constructor

Responsibilities:
- Construct system state
- Own time progression (via tick engine)
- Expose snapshot() for UI
- Coordinate prebirth, scuttling, embodiment, birth
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
from genesis.birth.criteria import BirthCriteria
from genesis.birth.transition import BirthTransitionEngine
from genesis.birth import BirthState

# -------------------------
# Embodiment
# -------------------------
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
        # Birth (FIXED)
        # -----------------
        "birth_criteria": BirthCriteria(),
        "birth_transition": BirthTransitionEngine(),
        "birth_state": None,

        # -----------------
        # Structural channels (written by tick)
        # -----------------
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,

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
            for name, g in (snap.gates or {}).items():
                gates[name] = g
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