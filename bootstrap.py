from __future__ import annotations
from typing import Callable

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.memory.structural_memory import StructuralMemory
from sandys_law_a7do.gates.engine import GateEngine
from sandys_law_a7do.scuttling.engine import ScuttlingEngine


def build_system() -> tuple[Callable[[], dict], dict]:
    state = {
        "ticks": 0,
        "frames": FrameStore(),
        "memory": StructuralMemory(),
        "gate_engine": GateEngine(),
        "scuttling": ScuttlingEngine(),
        "last_coherence": 0.0,
        "last_fragmentation": 0.0,
        "structural_load": 0.0,
    }

    def snapshot() -> dict:
        coherence = state["last_coherence"]
        load = state["structural_load"]

        return {
            "ticks": state["ticks"],
            "metrics": {
                "Z": state["last_fragmentation"],
                "Coherence": coherence,
                "Load": load,
                "Stability": coherence * (1.0 - load),
            },
            "embodiment_candidates": state["scuttling"].candidates_snapshot(),
        }

    return snapshot, state


def tick_system(state: dict) -> None:
    state["ticks"] += 1
    state["scuttling"].step()