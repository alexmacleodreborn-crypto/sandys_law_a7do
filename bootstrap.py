"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking
- Womb physics
- Scuttling growth
- Birth evaluation
- Dashboard-safe snapshots
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace

from sandys_law_a7do.gates.engine import GateEngine

# Embodiment (read-only)
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment

# Prebirth / Birth
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator

# Scuttling (PREBIRTH ONLY)
from sandys_law_a7do.scuttling.engine import ScuttlingEngine


# ============================================================
# SYSTEM BUILD
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    state = {
        # time
        "ticks": 0,

        # core systems
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # embodiment substrate (NO BEHAVIOUR)
        "embodiment_ledger": EmbodimentLedger(),

        # prebirth engines
        "womb_engine": WombPhysicsEngine(),
        "scuttling_engine": ScuttlingEngine(),

        # last read-only states
        "last_womb_state": None,
        "last_scuttling_candidates": [],

        # birth
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # structural metrics
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,
        "prediction_error": 0.0,
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (READ-ONLY)
# ============================================================

def system_snapshot(state: dict) -> dict:
    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    return {
        "ticks": int(state["ticks"]),
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
        },
        "active_frame": state["frames"].active,
        "memory_count": int(state["memory"].count()),
        "embodiment": summarize_embodiment(state["embodiment_ledger"]),
        "womb": state["last_womb_state"],
        "scuttling_candidates": state["last_scuttling_candidates"],
        "birth": (
            {
                "born": state["birth_state"].born,
                "reason": state["birth_state"].reason,
                "tick": state["birth_state"].tick,
            }
            if state.get("birth_state")
            else None
        ),
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "prebirth", label: str = "growth") -> None:
    if state["frames"].active is None:
        state["frames"].open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "phase", payload: dict | None = None) -> None:
    frame = state["frames"].active
    if frame:
        frame.add(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frames = state["frames"]
    frame = frames.active
    if frame is None:
        return

    # memory is positional only (safe)
    try:
        state["memory"].add_trace(
            MemoryTrace(
                state["ticks"],
                state["last_fragmentation"],
                state["last_coherence"],
                state["last_coherence"] * (1.0 - state["structural_load"]),
                f"{frame.domain}:{frame.label}",
                1.0,
                ["episode"],
            )
        )
    except Exception:
        pass

    state["structural_load"] *= 0.6
    frames.close()


# ============================================================
# TICK — AUTHORITATIVE CLOCK
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # -------------------------
    # WOMB
    # -------------------------
    womb = state["womb_engine"]
    state["last_womb_state"] = womb.step()

    # -------------------------
    # SCUTTLING (PREBIRTH ONLY)
    # -------------------------
    if state.get("birth_state") is None:
        scuttling = state["scuttling_engine"]
        scuttling.step()
        state["last_scuttling_candidates"] = scuttling.candidates_snapshot()

    # -------------------------
    # LOAD DYNAMICS
    # -------------------------
    if state["frames"].active:
        state["structural_load"] = min(1.0, state["structural_load"] + 0.05)
    else:
        state["structural_load"] *= 0.6

    # -------------------------
    # BIRTH EVALUATION
    # -------------------------
    if state.get("birth_state") is None:
        evaluator = state["birth_evaluator"]
        state["birth_state"] = evaluator.evaluate(
            tick=tick,
            metrics={
                "Stability": state["last_coherence"]
                * (1.0 - state["structural_load"]),
                "Load": state["structural_load"],
                "Z": state["last_fragmentation"],
            },
        )