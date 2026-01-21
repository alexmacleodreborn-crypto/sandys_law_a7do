# sandys_law_a7do/bootstrap.py

from typing import Callable, Tuple

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame
from sandys_law_a7do.frames.fragment import Fragment

from sandys_law_a7do.memory.structural_memory import StructuralMemory

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

    state = {
        "ticks": 0,

        # Frames
        "frames": FrameStore(),

        # Memory
        "memory": StructuralMemory(),

        # Structural channels
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "last_block_rate": 0.0,
        "structural_load": 0.0,

        # Prediction / preference channels
        "prediction_error": 0.0,
        "last_percept_notes": [],

        # Gates
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
    gate_engine: GateEngine = state.get("gate_engine")

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

    # -----------------------------
    # Gates
    # -----------------------------
    gate_view = {}

    if gate_engine:
        snap = gate_engine.snapshot()
        for name, gs in snap.gates.items():
            gate_view[name] = {
                "state": gs.result.state,
                "open": gs.open,
                "score": gs.result.score,
                "reason": gs.result.reason,
                "last_tick": gs.last_tick,
            }

    return {
        "ticks": state["ticks"],
        "metrics": metrics,
        "active_frame": frames.active,
        "memory_count": memory.count(),
        "prediction_error": state.get("prediction_error", 0.0),
        "gates": gate_view,
    }


# ============================================================
# FRAME OPERATIONS
# ============================================================

def open_frame(state: dict, *, domain: str = "demo", label: str = "ui"):
    frames: FrameStore = state["frames"]
    if frames.active:
        return
    frames.open(Frame(domain=domain, label=label))


def add_fragment(state: dict, *, kind: str = "contact", payload: dict | None = None):
    frames: FrameStore = state["frames"]
    frame = frames.active
    if not frame:
        return

    frag = Fragment(kind=kind, payload=payload or {})
    frames.add_fragment(frag)


def close_frame(state: dict):
    frames: FrameStore = state["frames"]
    frame = frames.active
    if not frame:
        return

    frames.close()

    coherence = float(state.get("last_coherence", 0.0))
    Z = float(state.get("last_fragmentation", 0.0))
    block_rate = float(state.get("last_block_rate", 0.0))
    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    gate_engine: GateEngine = state.get("gate_engine")

    if gate_engine:
        gate_engine.evaluate(
            coherence=coherence,
            fragmentation=Z,
            block_rate=block_rate,
            load=load,
        )

        stability_gate = gate_engine.get("stability")
    else:
        stability_gate = None

    memory: StructuralMemory = state["memory"]

    if stability_gate and stability_gate.open:
        memory.add_trace(
            tick=state["ticks"],
            Z=Z,
            coherence=coherence,
            stability=stability,
            frame_signature=f"{frame.domain}:{frame.label}",
            tags=["gated_consolidation"],
        )

    state["last_frame_closed"] = state["ticks"]