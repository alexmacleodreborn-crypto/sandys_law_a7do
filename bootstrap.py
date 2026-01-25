"""
Bootstrap — Phase 7.4 FINAL (LOCKED)

Responsibilities:
- Frame lifecycle
- Tick tracking
- Memory commit on frame close
- Gate evaluation at episode boundary
- Prebirth womb + scuttling (READ-ONLY)
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

# Embodiment (ledger is inert prebirth)
from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment

# Prebirth systems
from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator
from sandys_law_a7do.scuttling.engine import ScuttlingEngine


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

        # prebirth engines
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        "scuttling_engine": ScuttlingEngine(),

        # birth evaluator (STRUCTURAL ONLY)
        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # structural metrics (written by tick engine)
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
    gate_engine = state.get("gate_engine")
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in _get(snap, "gates", {}).items():
            gate_view[name] = _normalize_gate(gs)

    # -----------------------------
    # Embodiment ledger (read-only)
    # -----------------------------
    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

    # -----------------------------
    # Womb (read-only)
    # -----------------------------
    womb_view = None
    womb_state = state.get("last_womb_state")
    if womb_state:
        womb_view = {
            "tick": womb_state.tick,
            "heartbeat_rate": womb_state.heartbeat_rate,
            "ambient_load": womb_state.ambient_load,
            "rhythmic_stability": womb_state.rhythmic_stability,
            "womb_active": womb_state.womb_active,
        }

    # -----------------------------
    # Scuttling candidates (LOCAL)
    # -----------------------------
    candidates_view = []
    scuttling = state.get("scuttling_engine")
    if scuttling:
        candidates_view = scuttling.candidates_snapshot()

    # -----------------------------
    # Birth (read-only)
    # -----------------------------
    birth_view = None
    birth_state = state.get("birth_state")
    if birth_state:
        birth_view = {
            "born": birth_state.born,
            "reason": birth_state.reason,
            "tick": birth_state.tick,
        }

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": memory.count(),
        "prediction_error": state.get("prediction_error", 0.0),
        "gates": gate_view,
        "embodiment": embodiment_view,
        "embodiment_candidates": candidates_view,
        "womb": womb_view,
        "birth": birth_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "growth", label: str = "phase") -> None:
    frames: FrameStore = state["frames"]
    if frames.active is None:
        frames.open(Frame(domain=domain, label=label))


def add_fragment(
    state: dict,
    *,
    kind: str = "growth_phase",
    payload: dict | None = None,
) -> None:
    frames: FrameStore = state["frames"]
    if frames.active:
        frames.add(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    Z = state.get("last_fragmentation", 0.0)
    coherence = state.get("last_coherence", 0.0)
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
            tags=["prebirth"],
        )
    )

    frames.close()


# ============================================================
# TICK (TIME + PREBIRTH SYSTEMS)
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # womb physics
    womb = state.get("womb_engine")
    if womb:
        state["last_womb_state"] = womb.step()

    # scuttling growth
    scuttling = state.get("scuttling_engine")
    if scuttling:
        scuttling.step()

    # structural load decay
    frames: FrameStore = state["frames"]
    load = state.get("structural_load", 0.0)
    load = load + 0.05 if frames.active else load * 0.6
    state["structural_load"] = max(0.0, min(1.0, load))

    # birth evaluation
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