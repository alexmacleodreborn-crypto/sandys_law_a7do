"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking
- Structural metrics exposure
- Memory commit on frame close (Option A)
- Gate evaluation at episode boundary
- Dashboard-safe gate snapshot normalization

This file is AUTHORITATIVE.
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace

from sandys_law_a7do.gates.engine import GateEngine


# ============================================================
# SAFE ACCESS HELPERS (dict OR object)
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
        "ticks": 0,

        "frames": FrameStore(),
        "memory": StructuralMemory(),

        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "structural_load": 0.0,
        "prediction_error": 0.0,

        "gate_engine": GateEngine(),
    }

    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT
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

    gate_view: Dict[str, Dict[str, Any]] = {}

    if gate_engine:
        snap = gate_engine.snapshot()
        gates = _get(snap, "gates", {}) or {}
        for name, gs in gates.items():
            gate_view[str(name)] = _normalize_gate(gs)

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": int(memory.count()),
        "prediction_error": float(state.get("prediction_error", 0.0)),
        "gates": gate_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "demo", label: str = "ui") -> None:
    frames: FrameStore = state["frames"]
    if not frames.active:
        frames.open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "contact", payload: dict | None = None) -> None:
    frames: FrameStore = state["frames"]
    if frames.active:
        frames.add_fragment(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    """
    Episode boundary:
    - Commit memory
    - Evaluate gates
    """

    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    frame = frames.active
    if not frame:
        return

    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    prediction_error = float(state.get("prediction_error", 0.0))

    stability = coherence * (1.0 - load)

    # ✅ FIXED: positional-only MemoryTrace
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

    if gate_engine:
        gate_engine.evaluate(
            coherence=coherence,
            fragmentation=Z,
            load=load,
            prediction_error=prediction_error,
            tick=state["ticks"],
        )

    state["structural_load"] *= 0.6
    frames.close()


# ============================================================
# TICK
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1

    frames: FrameStore = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))