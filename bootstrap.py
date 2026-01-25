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
# SNAPSHOT (READ-ONLY, JSON SAFE)
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]
    gate_engine: GateEngine | None = state.get("gate_engine")

    # -----------------------------
    # Structural metrics
    # -----------------------------
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
    # Gates (READ-ONLY, SAFE)
    # -----------------------------
    gate_view: Dict[str, Dict[str, Any]] = {}

    if gate_engine is not None:
        snap = gate_engine.snapshot()
        gates = _get(snap, "gates", {}) or {}

        for name, g in gates.items():
            result = _get(g, "result", g)
            gate_view[str(name)] = {
                "state": _get(result, "state"),
                "open": bool(_get(result, "open")),
                "reason": _get(result, "reason"),
                "last_tick": int(_get(g, "last_tick", 0)),
            }

    # -----------------------------
    # Embodiment (READ-ONLY)
    # -----------------------------
    embodiment_view = None
    ledger = state.get("embodiment_ledger")
    if ledger is not None:
        embodiment_view = summarize_embodiment(ledger)

    # -----------------------------
    # Womb (READ-ONLY)
    # -----------------------------
    womb_view = None
    womb_state = state.get("last_womb_state")
    if womb_state is not None:
        womb_view = {
            "tick": int(_get(womb_state, "tick", 0)),
            "heartbeat_rate": float(_get(womb_state, "heartbeat_rate", 0.0)),
            "ambient_load": float(_get(womb_state, "ambient_load", 0.0)),
            "rhythmic_stability": float(_get(womb_state, "rhythmic_stability", 0.0)),
            "womb_active": bool(_get(womb_state, "womb_active", False)),
        }

    # -----------------------------
    # Birth (READ-ONLY)
    # -----------------------------
    birth_view = None
    birth_state = state.get("birth_state")
    if birth_state is not None:
        birth_view = {
            "born": bool(_get(birth_state, "born", False)),
            "reason": _get(birth_state, "reason"),
            "tick": int(_get(birth_state, "tick", 0)),
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


def add_fragment(
    state: dict,
    *,
    kind: str = "phase",
    payload: dict | None = None,
) -> None:
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