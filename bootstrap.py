"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking
- Memory commit on frame close
- Gate evaluation at episode boundary
- Dashboard-safe snapshots
- Prebirth womb environment (READ-ONLY)
- Birth evaluation (STRUCTURAL ONLY)
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

# Prebirth + Birth
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator


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

        # prebirth womb
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        # birth (STRUCTURAL ONLY)
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # development phase
        "current_phase": "prebirth",

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
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    coherence = float(state.get("last_coherence", 0.0))
    Z = float(state.get("last_fragmentation", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    metrics = {
        "Z": Z,
        "Coherence": coherence,
        "Stability": stability,
        "Load": load,
    }

    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

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
        "embodiment": embodiment_view,
        "womb": womb_view,
        "birth": birth_view,
        "phase": state["current_phase"],
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "development", label: str | None = None) -> None:
    frames: FrameStore = state["frames"]
    if frames.active is None:
        label = label or state.get("current_phase", "prebirth")
        frames.open(Frame(domain=domain, label=label))


def add_growth_event(state: dict, *, phase: str) -> None:
    """
    Add a STRUCTURAL growth impulse.
    """
    frames: FrameStore = state["frames"]
    if not frames.active:
        return

    fragment = Fragment(
        kind="growth",
        payload={
            "phase": phase,
            "tick": state["ticks"],
        },
    )
    frames.add_fragment(fragment)


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    coherence = state.get("last_coherence", 0.0)
    Z = state.get("last_fragmentation", 0.0)
    load = state.get("structural_load", 0.0)
    stability = coherence * (1.0 - load)

    memory.add_trace(
        MemoryTrace(
            tick=state["ticks"],
            Z=Z,
            coherence=coherence,
            stability=stability,
            frame_signature=f"{frame.domain}:{frame.label}",
            weight=1.0,
            tags=["development", state["current_phase"]],
        )
    )

    frames.close()


# ============================================================
# TICK (TIME + WOMB + BIRTH)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1

    # womb physics
    state["last_womb_state"] = state["womb_engine"].step()

    # structural load
    frames: FrameStore = state["frames"]
    if frames.active:
        state["structural_load"] = min(1.0, state["structural_load"] + 0.05)
    else:
        state["structural_load"] *= 0.6

    # birth evaluation
    if state["birth_state"] is None:
        evaluator: BirthEvaluator = state["birth_evaluator"]
        metrics = {
            "Stability": state.get("last_coherence", 0.0)
            * (1.0 - state.get("structural_load", 0.0)),
            "Load": state.get("structural_load", 1.0),
            "Z": state.get("last_fragmentation", 1.0),
        }
        bs = evaluator.evaluate(tick=state["ticks"], metrics=metrics)
        state["birth_state"] = bs
        if bs.born:
            state["current_phase"] = "postbirth"