from __future__ import annotations
from typing import Callable, Dict, Any, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame

from sandys_law_a7do.scuttling.engine import ScuttlingEngine
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator


# ============================================================
# SYSTEM BUILD
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    state = {
        # time
        "tick": 0,

        # core
        "frames": FrameStore(),

        # prebirth systems
        "womb": WombPhysicsEngine(),
        "scuttling": ScuttlingEngine(),

        # birth
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # structural channels
        "last_stability": 0.0,
        "last_load": 0.0,
        "last_fragmentation": 0.0,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (READ-ONLY)
# ============================================================

def system_snapshot(state: dict) -> dict:
    womb_state = state.get("womb_state")
    birth = state.get("birth_state")

    return {
        "tick": state["tick"],

        "womb": (
            {
                "heartbeat_rate": womb_state.heartbeat_rate,
                "ambient_load": womb_state.ambient_load,
                "rhythmic_stability": womb_state.rhythmic_stability,
                "active": womb_state.womb_active,
            }
            if womb_state else None
        ),

        "candidates": state["scuttling"].candidates_snapshot(),

        "birth": (
            {
                "born": birth.born,
                "reason": birth.reason,
                "tick": birth.tick,
            }
            if birth else None
        ),
    }