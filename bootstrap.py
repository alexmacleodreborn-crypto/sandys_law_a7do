# sandys_law_a7do/bootstrap.py

"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking
- Memory commit on frame close
- Gate evaluation at episode boundary
- Dashboard-safe snapshots

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

# NEW — embodiment (read-only)
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment


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
        "ticks": 0,

        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # NEW — embodiment substrate (no behaviour)
        "embodiment_ledger": EmbodimentLedger(),

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

    # OPTIONAL — read-only embodiment summary
    embodiment_view = None
    ledger = state.get("embodiment_ledger")
    if ledger is not None:
        embodiment_view = summarize_embodiment(ledger)

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": int(memory.count()),
        "prediction_error": float(state.get("prediction_error", 0.0)),
        "gates": gate_view,
        "embodiment": embodiment_view,  # visible, inert
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