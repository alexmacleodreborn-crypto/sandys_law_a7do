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

        # structural metrics (written elsewhere)
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

    # -----------------------------
    # Gates (read-only)
    # -----------------------------
    gate_view: Dict[str, Dict[str, Any]] = {}
    if gate_engine:
        snap = gate_engine.snapshot()
        gates = _get(snap, "gates", {}) or {}
        for name, gs in gates.items():
            gate_view[str(name)] = _normalize_gate(gs)

    # -----------------------------
    # Embodiment (read-only)
    # -----------------------------
    embodiment_view = None
    ledger = state.get("embodiment_ledger")
    if ledger is not None:
        embodiment_view = summarize_embodiment(ledger)

    # -----------------------------
    # Womb (read-only)
    # -----------------------------
    womb_view = None
    womb_state = state.get("last_womb_state")
    if womb_state is not None:
        womb_view = {
            "tick": womb_state.tick,
            "heartbeat_rate": womb_state.heartbeat_rate,
            "ambient_load": womb_state.ambient_load,
            "rhythmic_stability": womb_state.rhythmic_stability,
            "womb_active": womb_state.womb_active,
        }

    # -----------------------------
    # Birth (read-only)
    # -----------------------------
    birth_view = None
    birth_state = state.get("birth_state")
    if birth_state is not None:
        birth_view = {
            "born": birth_state.born,
            "reason": birth_state.reason,
            "tick": birth_state.tick,
        }

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": int(memory.count()),
        "prediction_error": float(state.get("prediction_error", 0.0)),
        "gates": gate_view,
        "embodiment": embodiment_view,
        "womb": womb_view,
        "birth": birth_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "demo", label: str = "ui") -> None:
    frames: FrameStore = state["frames"]
    if frames.active is None:
        frames.open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "contact", payload: dict | None = None) -> None:
    frames: FrameStore = state["frames"]
    if frames.active:
        frames.add_fragment(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    frame = frames.active
    if frame is None:
        return

    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
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
# TICK (TIME + WOMB + BIRTH ONLY)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # -----------------------------
    # Prebirth — womb physics
    # -----------------------------
    womb = state.get("womb_engine")
    if womb is not None:
        state["last_womb_state"] = womb.step()

    # -----------------------------
    # Structural load
    # -----------------------------
    frames: FrameStore = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))

    # -----------------------------
    # Birth evaluation (STRUCTURAL)
    # -----------------------------
    evaluator = state.get("birth_evaluator")
    if evaluator and state.get("birth_state") is None:
        metrics = {
            "Stability": state.get("last_coherence", 0.0)
            * (1.0 - state.get("structural_load", 0.0)),
            "Load": state.get("structural_load", 1.0),
            "Z": state.get("last_fragmentation", 1.0),
        }

        state["birth_state"] = evaluator.evaluate(
            tick=tick,
            metrics=metrics,
        )