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
# SAFE ACCESS HELPERS
# ============================================================

def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_gate(gs: Any) -> Dict[str, Any]:
    result = _get(gs, "result", gs)
    return {
        "state": _get(result, "state"),
        "open": _get(result, "open"),
        "score": _get(result, "score"),
        "reason": _get(result, "reason"),
        "last_tick": _get(gs, "last_tick"),
    }


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

        # prebirth womb (NO AGENCY)
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        # birth (STRUCTURAL ONLY)
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
    gate_engine: GateEngine | None = state.get("gate_engine")

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

    # Gates
    gate_view: Dict[str, Dict[str, Any]] = {}
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in (_get(snap, "gates", {}) or {}).items():
            gate_view[str(name)] = _normalize_gate(gs)

    # Embodiment (read-only)
    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

    # Womb (read-only)
    womb_view = None
    if state["last_womb_state"]:
        ws = state["last_womb_state"]
        womb_view = {
            "tick": ws.tick,
            "heartbeat_rate": ws.heartbeat_rate,
            "ambient_load": ws.ambient_load,
            "rhythmic_stability": ws.rhythmic_stability,
            "womb_active": ws.womb_active,
        }

    # Birth (read-only)
    birth_view = None
    if state["birth_state"]:
        bs = state["birth_state"]
        birth_view = {
            "born": bs.born,
            "reason": bs.reason,
            "tick": bs.tick,
        }

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": int(memory.count()),
        "prediction_error": float(state["prediction_error"]),
        "gates": gate_view,
        "embodiment": embodiment_view,
        "womb": womb_view,
        "birth": birth_view,
    }


# ============================================================
# FRAME OPERATIONS (PUBLIC API)
# ============================================================

def open_frame(state: dict, *, domain: str = "genesis", label: str = "phase") -> None:
    frames: FrameStore = state["frames"]
    if frames.active is None:
        frames.open(Frame(domain=domain, label=label))


def add_phase_signal(
    state: dict,
    *,
    phase: str,
    payload: dict | None = None,
) -> None:
    """
    Add a PHASE signal to the active frame.

    This replaces fragment-level UI semantics.
    """
    frames: FrameStore = state["frames"]
    if frames.active:
        frames.active.add(
            Fragment(
                kind="phase_signal",
                payload={
                    "phase": phase,
                    **(payload or {}),
                },
            )
        )


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    frame = frames.active
    if frame is None:
        return

    Z = float(state["last_fragmentation"])
    coherence = float(state["last_coherence"])
    load = float(state["structural_load"])
    stability = coherence * (1.0 - load)

    try:
        memory.add_trace(
            MemoryTrace(
                state["ticks"],
                Z,
                coherence,
                stability,
                f"{frame.domain}:{frame.label}",
                1.0,
                ["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
            )
        )
    except Exception:
        pass

    if gate_engine:
        try:
            gate_engine.evaluate(coherence, Z, load)
        except Exception:
            pass

    state["structural_load"] *= 0.6
    frames.close()


# ============================================================
# TICK (TIME + WOMB + BIRTH)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # Womb physics
    state["last_womb_state"] = state["womb_engine"].step()

    # Structural load decay / increase
    frames: FrameStore = state["frames"]
    load = float(state["structural_load"])
    state["structural_load"] = max(
        0.0,
        min(1.0, load + 0.05 if frames.active else load * 0.6),
    )

    # Birth evaluation
    if state["birth_state"] is None:
        evaluator: BirthEvaluator = state["birth_evaluator"]
        metrics = {
            "Stability": state["last_coherence"] * (1.0 - state["structural_load"]),
            "Load": state["structural_load"],
            "Z": state["last_fragmentation"],
        }
        state["birth_state"] = evaluator.evaluate(
            tick=tick,
            metrics=metrics,
        )