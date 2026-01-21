# sandys_law_a7do/bootstrap.py

from typing import Callable, Tuple

from sandys_law_a7do.frames.frame_stack import FrameStack
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.memory_store import MemoryStore

from sandys_law_a7do.engine.tick_engine import step_tick

from sandys_law_a7do.gates.engine import GateEngine


# ============================================================
# SYSTEM BOOTSTRAP
# ============================================================

def build_system() -> Tuple[Callable[[], dict], dict]:
    """
    Build the full A7DO system.

    Returns:
    - snapshot(): callable producing read-only system view
    - state: mutable system state
    """

    # ---------------------------------
    # CORE STATE
    # ---------------------------------
    state = {
        "ticks": 0,

        # Frames
        "frames": FrameStack(),

        # Memory
        "memory": MemoryStore(),

        # Structural metrics
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "structural_load": 0.0,

        # Prediction error
        "prediction_error": 0.0,

        # Preference / attention channels
        "last_percept_notes": [],

        # Gates
        "gate_engine": GateEngine(),
    }

    # ---------------------------------
    # SNAPSHOT FUNCTION
    # ---------------------------------
    def snapshot() -> dict:
        return system_snapshot(state)

    return snapshot, state


# ============================================================
# SNAPSHOT (READ-ONLY VIEW)
# ============================================================

def system_snapshot(state: dict) -> dict:
    frames = state["frames"]
    memory = state["memory"]
    gate_engine = state.get("gate_engine")

    # ---------------------------------
    # METRICS
    # ---------------------------------
    Z = float(state.get("last_fragmentation", 0.0))
    coherence = float(state.get("last_coherence", 0.0))
    block_rate = float(state.get("last_block_rate", 0.0))
    load = float(state.get("structural_load", 0.0))

    stability = coherence * (1.0 - load)

    metrics = {
        "Z": Z,
        "Coherence": coherence,
        "Stability": stability,
        "Load": load,
    }

    # ---------------------------------
    # GATES SNAPSHOT
    # ---------------------------------
    gate_view = {}

    if gate_engine is not None:
        snap = gate_engine.snapshot()

        for name, gs in snap.gates.items():
            gate_view[name] = {
                "state": gs.result.state,
                "open": gs.open,
                "score": gs.result.score,
                "reason": gs.result.reason,
                "last_tick": gs.last_tick,
            }

    # ---------------------------------
    # FINAL VIEW
    # ---------------------------------
    return {
        "ticks": state["ticks"],
        "metrics": metrics,

        "active_frame": frames.active,
        "memory_count": len(memory.traces),

        "prediction_error": state.get("prediction_error", 0.0),

        "gates": gate_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "demo", label: str = "ui"):
    frames: FrameStack = state["frames"]
    frames.open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "contact", payload: dict | None = None):
    frames: FrameStack = state["frames"]
    frame = frames.active

    if frame is None:
        return

    frag = Fragment(
        kind=kind,
        payload=payload or {},
    )
    frame.add_fragment(frag)


def close_frame(state: dict):
    """
    Close the active frame.

    STEP 1 GATING:
    - Evaluate gates
    - Consolidate memory ONLY if stability gate is open
    """

    frames: FrameStack = state["frames"]
    frame = frames.active

    if frame is None:
        return

    # ---------------------------------
    # CLOSE FRAME STRUCTURALLY
    # ---------------------------------
    frames.close_active()

    # ---------------------------------
    # READ METRICS
    # ---------------------------------
    coherence = float(state.get("last_coherence", 0.0))
    Z = float(state.get("last_fragmentation", 0.0))
    block_rate = float(state.get("last_block_rate", 0.0))
    load = float(state.get("structural_load", 0.0))

    stability = coherence * (1.0 - load)

    # ---------------------------------
    # GATE EVALUATION
    # ---------------------------------
    gate_engine: GateEngine = state.get("gate_engine")

    if gate_engine is not None:
        gate_engine.evaluate(
            coherence=coherence,
            fragmentation=Z,
            block_rate=block_rate,
            load=load,
        )

        stability_gate = gate_engine.get("stability")
    else:
        stability_gate = None

    # ---------------------------------
    # MEMORY CONSOLIDATION (GATED)
    # ---------------------------------
    memory: MemoryStore = state.get("memory")

    if (
        memory is not None
        and stability_gate is not None
        and stability_gate.open
    ):
        memory.consolidate(
            tick=state["ticks"],
            Z=Z,
            coherence=coherence,
            stability=stability,
            frame_signature=frame.signature,
            tags=["auto_consolidated"],
        )

    # ---------------------------------
    # CLEANUP
    # ---------------------------------
    state["last_frame_closed"] = state["ticks"]