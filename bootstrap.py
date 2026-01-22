"""
Bootstrap — Gate Snapshot SAFE (LOCKED)

Fixes:
- New Frame must always open immediately (doorman behaviour)
- Close Frame MUST commit episode memory (Option A)
- Gate snapshots may be dicts OR objects
- Dashboard-safe gate normalization

Keeps:
- FrameStore lifecycle
- Tick state
- Structural channels
- Memory + gates exposure
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


def _normalize_gate_state(gs: Any) -> Dict[str, Any]:
    """
    Normalise a gate snapshot into a dashboard-safe dict.
    Works whether gate snapshots are dicts or dataclasses.
    """
    result = _get(gs, "result", gs)

    return {
        "state": _get(result, "state", None),
        "open": _get(result, "open", _get(gs, "open", None)),
        "score": _get(result, "score", _get(gs, "score", None)),
        "reason": _get(result, "reason", _get(gs, "reason", None)),
        "last_tick": _get(gs, "last_tick", None),
    }


# ============================================================
# SYSTEM BOOTSTRAP
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    """
    Returns:
      snapshot() -> dict
      state -> mutable dict
    """

    state = {
        # time
        "ticks": 0,

        # frames
        "frames": FrameStore(),

        # memory
        "memory": StructuralMemory(),

        # structural channels (written by tick engine)
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
    """
    Doorman behaviour:
    - If no frame exists, OPEN immediately
    """
    frames: FrameStore = state["frames"]

    if frames.active is None:
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

    frag = Fragment(kind=kind, payload=payload or {})
    frames.add_fragment(frag)


def close_frame(state: dict) -> None:
    """
    OPTION A — EPISODE COMMIT ON FRAME CLOSE

    This is the ONLY place memory is written.
    """

    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    # ----------------------------------
    # EPISODE METRICS (AUTHORITATIVE)
    # ----------------------------------
    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    trace = MemoryTrace(
        state["ticks"],
        Z,
        coherence,
        stability,
        f"{frame.domain}:{frame.label}",
        1.0,
        ["episode", "stable"] if stability >= 0.7 else ["episode", "unstable"],
    )

    memory.add_trace(trace)

    # ----------------------------------
    # RELEASE STRUCTURAL PRESSURE
    # ----------------------------------
    state["structural_load"] *= 0.6

    # ----------------------------------
    # CLOSE FRAME
    # ----------------------------------
    frames.close()


# ============================================================
# TICK (PURE TIME ADVANCE)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1