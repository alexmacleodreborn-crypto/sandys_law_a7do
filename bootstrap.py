"""
Bootstrap — Phase 7.4 STABLE

Responsibilities:
- Frame lifecycle
- Tick tracking
- Structural metrics
- Memory commit on frame close
- Gate evaluation
- Prebirth womb physics (READ-ONLY)
- Birth evaluation (STRUCTURAL ONLY)
- Snapshot-safe serialization
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace

from sandys_law_a7do.gates.engine import GateEngine

# Embodiment (read-only substrate)
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment

# Prebirth / Birth
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator


# ============================================================
# SAFE ACCESS
# ============================================================

def _get(obj: Any, key: str, default: Any = None) -> Any:
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

        # core
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # embodiment substrate (NO BEHAVIOR)
        "embodiment_ledger": EmbodimentLedger(),

        # prebirth
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

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
# SNAPSHOT (JSON SAFE)
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # ---- metrics
    metrics = {
        "Z": round(Z, 4),
        "Coherence": round(coherence, 4),
        "Stability": round(stability, 4),
        "Load": round(load, 4),
    }

    # ---- gates
    gate_view = {}
    ge = state.get("gate_engine")
    if ge:
        snap = ge.snapshot()
        for name, g in (snap.get("gates") or {}).items():
            res = _get(g, "result", {})
            gate_view[str(name)] = {
                "state": _get(res, "state"),
                "open": bool(_get(res, "open")),
                "reason": _get(res, "reason"),
                "last_tick": int(_get(g, "last_tick", 0)),
            }

    # ---- embodiment (read-only)
    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

    # ---- womb (JSON SAFE)
    womb_view = None
    ws = state.get("last_womb_state")
    if ws is not None:
        womb_view = {
            "tick": int(ws.tick),
            "heartbeat_rate": float(ws.heartbeat_rate),
            "ambient_load": float(ws.ambient_load),
            "rhythmic_stability": float(ws.rhythmic_stability),
            "womb_active": bool(ws.womb_active),
        }

    # ---- birth
    birth_view = None
    bs = state.get("birth_state")
    if bs is not None:
        birth_view = {
            "born": bool(bs.born),
            "reason": str(bs.reason),
            "tick": int(bs.tick),
        }

    return {
        "ticks": int(state["ticks"]),
        "metrics": metrics,
        "active_frame": (
            f"{frames.active.domain}:{frames.active.label}"
            if frames.active else None
        ),
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

def open_frame(state: dict, *, domain: str = "prebirth", label: str = "auto") -> None:
    if state["frames"].active is None:
        state["frames"].open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "phase", payload: dict | None = None) -> None:
    frame = state["frames"].active
    if frame:
        frame.add(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frames = state["frames"]
    frame = frames.active
    if frame is None:
        return

    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    try:
        state["memory"].add_trace(
            MemoryTrace(
                tick=state["ticks"],
                Z=Z,
                coherence=coherence,
                stability=stability,
                frame_signature=f"{frame.domain}:{frame.label}",
                weight=1.0,
                tags=["episode"],
            )
        )
    except Exception:
        pass

    state["structural_load"] *= 0.6
    frames.close()


# ============================================================
# TICK — TIME + WOMB + BIRTH ONLY
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # womb physics
    womb = state.get("womb_engine")
    if womb:
        state["last_womb_state"] = womb.step()

    # structural load
    if state["frames"].active:
        state["structural_load"] = min(1.0, state["structural_load"] + 0.05)
    else:
        state["structural_load"] *= 0.6

    # birth evaluation
    if state["birth_state"] is None:
        evaluator = state["birth_evaluator"]
        state["birth_state"] = evaluator.evaluate(
            tick=tick,
            metrics={
                "Stability": state["last_coherence"] * (1.0 - state["structural_load"]),
                "Load": state["structural_load"],
                "Z": state["last_fragmentation"],
            },
        )