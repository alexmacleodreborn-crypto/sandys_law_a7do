"""
Bootstrap — Phase 7.4 (STABLE)

Responsibilities:
- Authoritative time
- Prebirth womb stepping
- Scuttling embodied growth
- Structural metrics exposure
- Birth evaluation (read-only)
- Dashboard-safe snapshot

NO cognition
NO consolidation
NO embodiment writes
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.gates.engine import GateEngine

from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment

from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator

from sandys_law_a7do.scuttling.engine import ScuttlingEngine


# ------------------------------------------------------------
# System Build
# ------------------------------------------------------------

def build_system() -> Tuple[Callable[[], dict], dict]:
    state = {
        "ticks": 0,

        # core
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # embodiment (read-only)
        "embodiment_ledger": EmbodimentLedger(),

        # prebirth
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        # scuttling (prebirth body)
        "scuttling_engine": ScuttlingEngine(),

        # birth
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # structural channels
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,
        "prediction_error": 0.0,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ------------------------------------------------------------
# Snapshot (READ-ONLY)
# ------------------------------------------------------------

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]

    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    metrics = {
        "Z": Z,
        "Coherence": coherence,
        "Stability": stability,
        "Load": load,
    }

    # embodiment (ledger)
    embodiment = summarize_embodiment(state["embodiment_ledger"])

    # womb
    womb_state = state.get("last_womb_state")
    womb = None
    if womb_state:
        womb = {
            "tick": womb_state.tick,
            "heartbeat_rate": womb_state.heartbeat_rate,
            "ambient_load": womb_state.ambient_load,
            "rhythmic_stability": womb_state.rhythmic_stability,
            "womb_active": womb_state.womb_active,
        }

    # scuttling
    scuttling = state["scuttling_engine"]
    scuttling_view = {
        "regions": scuttling.graph.snapshot(),
        "candidates": scuttling.candidates_snapshot(),
    }

    # birth
    birth = None
    if state["birth_state"]:
        birth = {
            "born": state["birth_state"].born,
            "reason": state["birth_state"].reason,
            "tick": state["birth_state"].tick,
        }

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "active_frame": frames.active,
        "embodiment": embodiment,
        "womb": womb,
        "scuttling": scuttling_view,
        "birth": birth,
    }


# ------------------------------------------------------------
# Frame Operations
# ------------------------------------------------------------

def open_frame(state: dict, *, domain: str = "prebirth", label: str = "growth") -> None:
    if state["frames"].active is None:
        state["frames"].open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "phase", payload: dict | None = None) -> None:
    frame = state["frames"].active
    if frame:
        frame.add(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    state["frames"].close()


# ------------------------------------------------------------
# Tick (AUTHORITATIVE)
# ------------------------------------------------------------

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # womb
    state["last_womb_state"] = state["womb_engine"].step()

    # scuttling
    state["scuttling_engine"].step()

    # load decay
    load = state.get("structural_load", 0.0)
    state["structural_load"] = max(0.0, min(1.0, load * 0.9))

    # birth evaluation
    if state["birth_state"] is None:
        evaluator = state["birth_evaluator"]
        metrics = {
            "Stability": state["last_coherence"] * (1.0 - state["structural_load"]),
            "Load": state["structural_load"],
            "Z": state["last_fragmentation"],
        }
        state["birth_state"] = evaluator.evaluate(
            tick=tick,
            metrics=metrics,
        )