"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking (authoritative)
- Prebirth womb physics
- Scuttling (local growth)
- Birth evaluation (structural only)
- Read-only snapshots for dashboard
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.gates.engine import GateEngine

# Embodiment (INERT until birth)
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment

# Genesis
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator

# Scuttling (LOCAL growth)
from sandys_law_a7do.scuttling.engine import ScuttlingEngine


# ============================================================
# SAFE ACCESS
# ============================================================

def _get(obj: Any, key: str, default=None):
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


# ============================================================
# SYSTEM BUILD
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    state = {
        # time
        "ticks": 0,

        # core runtime
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # embodiment (EMPTY until birth)
        "embodiment_ledger": EmbodimentLedger(),

        # genesis
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        # scuttling (ACTIVE prebirth)
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


# ============================================================
# SNAPSHOT (READ-ONLY)
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

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

    # -----------------------------
    # Embodiment (empty prebirth)
    # -----------------------------
    embodiment_view = summarize_embodiment(
        state["embodiment_ledger"]
    )

    # -----------------------------
    # Local embodiment (PREBIRTH)
    # -----------------------------
    local_embodiment = None
    if state.get("birth_state") is None:
        local_embodiment = state["scuttling_engine"].candidates_snapshot()

    # -----------------------------
    # Womb
    # -----------------------------
    womb_view = None
    if state.get("last_womb_state"):
        ws = state["last_womb_state"]
        womb_view = {
            "tick": ws.tick,
            "heartbeat_rate": ws.heartbeat_rate,
            "ambient_load": ws.ambient_load,
            "rhythmic_stability": ws.rhythmic_stability,
            "womb_active": ws.womb_active,
        }

    # -----------------------------
    # Birth
    # -----------------------------
    birth_view = None
    if state.get("birth_state"):
        bs = state["birth_state"]
        birth_view = {
            "born": bs.born,
            "reason": bs.reason,
            "tick": bs.tick,
        }

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": memory.count(),
        "prediction_error": state.get("prediction_error", 0.0),

        "womb": womb_view,
        "birth": birth_view,

        "local_embodiment": local_embodiment,
        "embodiment": embodiment_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain="demo", label="ui") -> None:
    if state["frames"].active is None:
        state["frames"].open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind="phase", payload=None) -> None:
    if state["frames"].active:
        state["frames"].active.add(
            Fragment(kind=kind, payload=payload or {})
        )


def close_frame(state: dict) -> None:
    frames = state["frames"]
    if not frames.active:
        return

    Z = state["last_fragmentation"]
    coherence = state["last_coherence"]
    load = state["structural_load"]
    stability = coherence * (1.0 - load)

    try:
        state["memory"].add_trace(
            MemoryTrace(
                state["ticks"],
                Z,
                coherence,
                stability,
                f"{frames.active.domain}:{frames.active.label}",
                1.0,
                ["episode"],
            )
        )
    except Exception:
        pass

    state["structural_load"] *= 0.6
    frames.close()


# ============================================================
# TICK — AUTHORITATIVE
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # womb physics
    state["last_womb_state"] = state["womb_engine"].step()

    # scuttling (ONLY if not born)
    if state.get("birth_state") is None:
        state["scuttling_engine"].step()

    # structural load
    if state["frames"].active:
        state["structural_load"] = min(1.0, state["structural_load"] + 0.05)
    else:
        state["structural_load"] *= 0.6

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