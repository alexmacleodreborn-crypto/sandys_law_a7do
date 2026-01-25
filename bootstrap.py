# sandys_law_a7do/bootstrap.py

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
- Embodiment candidate growth (AUTOMATIC)
- Embodiment consolidation (POST-BIRTH ONLY)

AUTHORITATIVE FILE
"""

from __future__ import annotations
from typing import Any, Callable, Dict, Tuple

# ------------------------------------------------------------
# Core
# ------------------------------------------------------------

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.memory.trace import MemoryTrace

from sandys_law_a7do.gates.engine import GateEngine

# ------------------------------------------------------------
# Embodiment (STRUCTURAL ONLY)
# ------------------------------------------------------------

from embodiment.ledger.ledger import EmbodimentLedger
from embodiment.bridge.accountant import summarize_embodiment
from embodiment.local.candidates import CandidateBuilder
from embodiment.consolidation.gate import ConsolidationGate

# ------------------------------------------------------------
# Genesis
# ------------------------------------------------------------

from genesis.womb.physics import WombPhysicsEngine
from genesis.birth import BirthEvaluator

# ------------------------------------------------------------
# Scuttling
# ------------------------------------------------------------

from scuttling.coupling import CouplingGraph, CouplingSignal


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
        # ----------------------------------------------------
        # Time
        # ----------------------------------------------------
        "ticks": 0,

        # ----------------------------------------------------
        # Core runtime
        # ----------------------------------------------------
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),

        # ----------------------------------------------------
        # Embodiment substrate (NO BEHAVIOUR)
        # ----------------------------------------------------
        "embodiment_ledger": EmbodimentLedger(),
        "candidate_builder": CandidateBuilder(),
        "consolidation_gate": ConsolidationGate(),
        "pending_candidates": [],

        # ----------------------------------------------------
        # Scuttling (LOCAL PHYSIOLOGY)
        # ----------------------------------------------------
        "scuttling_graph": CouplingGraph(),

        # ----------------------------------------------------
        # Prebirth + Birth
        # ----------------------------------------------------
        "womb_engine": WombPhysicsEngine(),
        "last_womb_state": None,

        "birth_evaluator": BirthEvaluator(),
        "birth_state": None,

        # ----------------------------------------------------
        # Structural metrics (written elsewhere)
        # ----------------------------------------------------
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
    # Gates
    # -----------------------------
    gate_view = {}
    gate_engine = state.get("gate_engine")
    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in _get(snap, "gates", {}).items():
            gate_view[name] = _normalize_gate(gs)

    # -----------------------------
    # Embodiment
    # -----------------------------
    embodiment_view = summarize_embodiment(state["embodiment_ledger"])

    # -----------------------------
    # Womb
    # -----------------------------
    womb_view = None
    womb = state.get("last_womb_state")
    if womb:
        womb_view = {
            "tick": womb.tick,
            "heartbeat_rate": womb.heartbeat_rate,
            "ambient_load": womb.ambient_load,
            "rhythmic_stability": womb.rhythmic_stability,
            "womb_active": womb.womb_active,
        }

    # -----------------------------
    # Birth
    # -----------------------------
    birth_view = None
    birth = state.get("birth_state")
    if birth:
        birth_view = {
            "born": birth.born,
            "reason": birth.reason,
            "tick": birth.tick,
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
        "pending_candidates": len(state["pending_candidates"]),
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "prebirth", label: str = "growth") -> None:
    if state["frames"].active is None:
        state["frames"].open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str, payload: dict | None = None) -> None:
    frame = state["frames"].active
    if frame:
        frame.add_fragment(Fragment(kind=kind, payload=payload or {}))


def close_frame(state: dict) -> None:
    frame = state["frames"].active
    if frame is None:
        return

    # --------------------------------------------------------
    # 1. MEMORY (STRUCTURAL TRACE)
    # --------------------------------------------------------
    Z = state["last_fragmentation"]
    coherence = state["last_coherence"]
    load = state["structural_load"]
    stability = coherence * (1.0 - load)

    try:
        state["memory"].add_trace(
            MemoryTrace(
                state["ticks"],
                Z,
                coherence,
                stability,
                f"{frame.domain}:{frame.label}",
                1.0,
                ["episode"],
            )
        )
    except Exception:
        pass

    # --------------------------------------------------------
    # 2. SCUTTLING → EMBODIMENT CANDIDATES
    # --------------------------------------------------------
    graph = state["scuttling_graph"]

    for frag in frame.fragments:
        region = frag.payload.get("region", "torso")
        if frag.kind == "womb_pressure":
            graph.propagate_up(
                CouplingSignal("load", frag.payload.get("load", 0.1), region)
            )
        elif frag.kind == "limb_contact":
            graph.propagate_up(
                CouplingSignal("pain", frag.payload.get("pressure", 0.1), region)
            )

    snapshot = graph.snapshot()

    candidates = state["candidate_builder"].build_from_coupling(
        snapshot=snapshot,
        support=1,
    )

    state["pending_candidates"].extend(candidates)

    # --------------------------------------------------------
    # 3. CONSOLIDATION (ONLY AFTER BIRTH)
    # --------------------------------------------------------
    if state.get("birth_state") and state["birth_state"].born:
        ledger = state["embodiment_ledger"]
        gate = state["consolidation_gate"]

        for c in list(state["pending_candidates"]):
            decision = gate.evaluate(candidate=c, ledger=ledger)
            if decision.accepted:
                state["pending_candidates"].remove(c)

    state["structural_load"] *= 0.6
    state["frames"].close()


# ============================================================
# TICK — TIME + WOMB + BIRTH ONLY
# ============================================================

def tick_system(state: dict) -> None:
    state["ticks"] += 1
    tick = state["ticks"]

    # -----------------------------
    # Womb physics
    # -----------------------------
    womb = state.get("womb_engine")
    if womb:
        state["last_womb_state"] = womb.step()

    # -----------------------------
    # Load decay / accumulation
    # -----------------------------
    if state["frames"].active:
        state["structural_load"] += 0.05
    else:
        state["structural_load"] *= 0.6

    state["structural_load"] = min(1.0, max(0.0, state["structural_load"]))

    # -----------------------------
    # Birth evaluation
    # -----------------------------
    evaluator = state["birth_evaluator"]
    if state["birth_state"] is None:
        metrics = {
            "Stability": state["last_coherence"] * (1.0 - state["structural_load"]),
            "Load": state["structural_load"],
            "Z": state["last_fragmentation"],
        }
        state["birth_state"] = evaluator.evaluate(tick=tick, metrics=metrics)