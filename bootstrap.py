# sandys_law_a7do/bootstrap.py
"""
Bootstrap — Gate Snapshot SAFE (LOCKED)

Fix:
- GateEngine.snapshot() may return dict-based gate snapshots (not dataclasses).
- This bootstrap normalizes either dict OR object structures into a single view.

Keeps:
- FrameStore lifecycle
- Tick state
- Memory + metrics exposure
- Gates exposure in dashboard-safe dict format
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory

from sandys_law_a7do.gates.engine import GateEngine


# ============================================================
# Small safe getters (dict OR object)
# ============================================================

def _get(obj: Any, key: str, default: Any = None) -> Any:
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _normalize_gate_state(gs: Any) -> Dict[str, Any]:
    """
    Normalize a single gate snapshot into a dashboard-safe dict.

    Guaranteed keys:
      - state
      - open
      - score
      - reason
      - last_tick
    """

    result = _get(gs, "result", None)
    if result is None:
        result = gs

    state = _get(result, "state", _get(gs, "state", None))
    reason = _get(result, "reason", _get(gs, "reason", None))
    score = _get(result, "score", _get(gs, "score", None))
    last_tick = _get(gs, "last_tick", None)

    open_flag = _get(gs, "open", None)
    if open_flag is None and isinstance(state, str):
        open_flag = state == "allow"

    return {
        "state": state,
        "open": bool(open_flag) if open_flag is not None else False,
        "score": float(score) if isinstance(score, (int, float)) else None,
        "reason": reason,
        "last_tick": last_tick,
    }


# ============================================================
# SYSTEM BOOTSTRAP
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    state = {
        "ticks": 0,

        # frames
        "frames": FrameStore(),

        # memory
        "memory": StructuralMemory(),

        # structural channels
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "structural_load": 0.0,

        # optional extra channels
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

    if gate_engine:
        snap = gate_engine.snapshot()
        gates = _get(snap, "gates", {}) or {}

        if isinstance(gates, dict):
            for name, gs in gates.items():
                gate_view[str(name)] = _normalize_gate_state(gs)

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


def add_fragment(state: dict, *, kind: str = "contact", payload: dict | None = None) -> None:
    frames: FrameStore = state["frames"]
    if not frames.active:
        return
    frames.add_fragment(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    if frames.active:
        frames.close()


def tick_system(state: dict) -> None:
    state["ticks"] += 1