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

AUTHORITATIVE FILE
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame

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
        "ticks": 0,

        # Core systems
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # Embodiment substrate (NO BEHAVIOUR)
        "embodiment_ledger": EmbodimentLedger(),

        # Prebirth womb (NO AGENCY)
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        # Birth (STRUCTURAL ONLY)
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # Structural metrics (written elsewhere)
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

    # Embodiment (read-only)
    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

    # Womb (read-only)
    womb_view = None
    if state["last_womb_state"] is not None:
        w = state["last_womb_state"]
        womb_view = {
            "tick": w.tick,
            "heartbeat_rate": w.heartbeat_rate,
            "ambient_load": w.ambient_load,
            "rhythmic_stability": w.rhythmic_stability,
            "womb_active": w.womb_active,
        }

    # Birth (read-only)
    birth_view = None
    if state["birth_state"] is not None:
        b = state["birth_state"]
        birth_view = {
            "born": b.born,
            "reason": b.reason,
            "tick": b.tick,
        }

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": int(state["memory"].count()),
        "prediction_error": float(state.get("prediction_error", 0.0)),
        "embodiment": embodiment_view,
        "womb": womb_view,
        "birth": birth_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "development", label: str = "prebirth") -> None:
    frames: FrameStore = state["frames"]
    if frames.active is None:
        frames.open(Frame(domain=domain, label=label))


def add_phase(state: dict, *, phase: str = "prebirth_growth") -> None:
    """
    Add a developmental phase to the active frame.
    """
    frames: FrameStore = state["frames"]
    frame = frames.active
    if frame is None:
        return

    frame.add_phase({
        "phase": phase,
        "tick": state["ticks"],
    })


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    frame = frames.active
    if frame is None:
        return

    # Memory commit (structural only)
    stability = state["last_coherence"] * (1.0 - state["structural_load"])

    try:
        state["memory"].add_trace(
            MemoryTrace(
                state["ticks"],
                state["last_fragmentation"],
                state["last_coherence"],
                stability,
                f"{frame.domain}:{frame.label}",
                1.0,
                ["episode"],
            )
        )
    except Exception:
        pass

    frames.close()


# ============================================================
# TICK (TIME + WOMB + BIRTH)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # Womb physics
    state["last_womb_state"] = state["womb_engine"].step()

    # Structural load
    frames: FrameStore = state["frames"]
    load = state["structural_load"]
    load = load + 0.05 if frames.active else load * 0.6
    state["structural_load"] = max(0.0, min(1.0, load))

    # Birth evaluation
    if state["birth_state"] is None:
        metrics = {
            "Stability": state["last_coherence"] * (1.0 - state["structural_load"]),
            "Load": state["structural_load"],
            "Z": state["last_fragmentation"],
        }
        state["birth_state"] = state["birth_evaluator"].evaluate(
            tick=tick,
            metrics=metrics,
        )