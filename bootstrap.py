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
import inspect

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
    """
    Normalize a gate snapshot into dashboard-safe dict.
    """
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
    """
    Returns:
      snapshot() -> dict
      state -> mutable system state
    """

    state = {
        # time
        "ticks": 0,

        # core
        "frames": FrameStore(),
        "memory": StructuralMemory(),

        # structural channels
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "structural_load": 0.0,
        "prediction_error": 0.0,

        # gates
        "gate_engine": GateEngine(),
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

    gate_view: Dict[str, Dict[str, Any]] = {}

    if gate_engine is not None:
        snap = gate_engine.snapshot()
        gates = _get(snap, "gates", {}) or {}

        if isinstance(gates, dict):
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
    if frames.active:
        return
    frames.open(Frame(domain=domain, label=label))


def add_fragment(
    state: dict,
    *,
    kind: str = "contact",
    payload: dict | None = None,
) -> None:
    frames: FrameStore = state["frames"]
    if not frames.active:
        return
    frames.add_fragment(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    """
    OPTION A — Episode boundary
    """

    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    frame = frames.active
    if not frame:
        return

    # -----------------------------
    # STRUCTURAL READOUT
    # -----------------------------
    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    prediction_error = float(state.get("prediction_error", 0.0))

    stability = coherence * (1.0 - load)

    # -----------------------------
    # MEMORY COMMIT
    # -----------------------------
    memory.add_trace(
        MemoryTrace(
            tick=state["ticks"],
            fragmentation=Z,
            coherence=coherence,
            stability=stability,
            context=f"{frame.domain}:{frame.label}",
            weight=1.0,
            tags=["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
        )
    )

    # -----------------------------
    # 🔑 SAFE GATE EVALUATION
    # -----------------------------
    if gate_engine is not None:
        try:
            sig = inspect.signature(gate_engine.evaluate)
            kwargs = {}

            for name in sig.parameters:
                if name == "coherence":
                    kwargs[name] = coherence
                elif name == "fragmentation":
                    kwargs[name] = Z
                elif name == "load":
                    kwargs[name] = load
                elif name == "prediction_error":
                    kwargs[name] = prediction_error
                elif name == "tick":
                    kwargs[name] = state["ticks"]

            gate_engine.evaluate(**kwargs)

        except Exception:
            # Gates must NEVER crash the system
            pass

    # -----------------------------
    # RELEASE PRESSURE
    # -----------------------------
    state["structural_load"] *= 0.6

    frames.close()


# ============================================================
# TICK (TIME ONLY)
# ============================================================

def tick_system(state: dict) -> None:
    """
    Tick advances time and structural pressure.
    """
    state["ticks"] += 1

    frames: FrameStore = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))