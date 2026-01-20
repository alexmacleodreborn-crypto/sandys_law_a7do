# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (FINAL, CONTRACT-CORRECT)
"""

from roles.system_manager import SystemManager
from roles.sled_interface import SLEDInterface

from frames.store import FrameStore
from frames.frame import Frame
from frames.fragment import Fragment

from memory.structural_memory import StructuralMemory
from embodiment.ledger import EmbodimentLedger
from embodiment.boundaries import BoundaryState

from mind.preference import PreferenceEngine
from mind.perception import summarize_perception
from mind.coherence import compute_coherence
from mind.regulation import regulate

from accounting.metrics import metric_bundle


# =========================================================
# SYSTEM CONSTRUCTION
# =========================================================

def build_system():
    frames_store = FrameStore()
    memory = StructuralMemory()
    embodiment_ledger = EmbodimentLedger()
    boundaries = BoundaryState()
    preferences = PreferenceEngine()

    ticks = 0
    last_closed_frame = None  # for inspection

    system = SystemManager()
    sled = SLEDInterface()
    system.register(sled)

    # -----------------------------------------------------
    # SNAPSHOT (READ-ONLY)
    # -----------------------------------------------------
    def snapshot():
        nonlocal ticks, last_closed_frame

        # Collect fragments from active + last closed frame
        frames = []
        if frames_store.active:
            frames.append(frames_store.active)
        if last_closed_frame:
            frames.append(last_closed_frame)

        # --- Perception ---
        fragments = []
        for f in frames:
            for frag in f.fragments:
                fragments.append({"action": frag.kind})

        percept = summarize_perception(fragments)

        # --- Boundary → block proxy ---
        hard_pressure = getattr(boundaries, "hard_pressure", 0.0)
        blocked_events = int(hard_pressure * 10)

        # --- Coherence ---
        coherence = compute_coherence(
            fragment_count=percept.fragment_count,
            unique_actions=percept.unique_actions,
            blocked_events=blocked_events,
        )

        # --- Regulation ---
        regulation = regulate(
            coherence=coherence.coherence,
            fragmentation=coherence.fragmentation,
            block_rate=coherence.block_rate,
        )

        # --- Metrics ---
        metrics = metric_bundle(
            {
                "Z": coherence.fragmentation,
                "Sigma": coherence.coherence,
                "Stability": 1.0 - coherence.fragmentation,
                "Coherence": coherence.coherence,
            }
        )

        return {
            "roles": list(system.roles.keys()),
            "ticks": ticks,
            "active_frame": frames_store.active,
            "last_frame": last_closed_frame,
            "metrics": metrics,
            "regulation": {
                "decision": regulation.decision,
                "reason": regulation.reason,
            },
        }

    state = {
        "frames_store": frames_store,
        "boundaries": boundaries,
        "memory": memory,
        "preferences": preferences,
        "_get_ticks": lambda: ticks,
        "_set_ticks": lambda v: None,
        "_set_last_frame": lambda f: None,
    }

    def _set_ticks(v):
        nonlocal ticks
        ticks = v

    def _set_last_frame(f):
        nonlocal last_closed_frame
        last_closed_frame = f

    state["_set_ticks"] = _set_ticks
    state["_set_last_frame"] = _set_last_frame

    return system, snapshot, state


# =========================================================
# CONTROLLED ACTIONS (UI CALLABLE)
# =========================================================

def inject_demo_frame(state):
    """
    Open a new demo frame.
    """
    frames_store = state["frames_store"]

    if frames_store.active:
        return None  # cannot open two frames

    frame = Frame(domain="demo", label="ui")
    frames_store.open(frame)
    return frame


def add_fragment(state):
    """
    Add a demo fragment to active frame.
    """
    frames_store = state["frames_store"]

    frag = Fragment(kind="demo", payload={"source": "ui"})
    frames_store.add_fragment(frag)
    return frag


def close_frame(state):
    """
    Close the active frame.
    """
    frames_store = state["frames_store"]
    frame = frames_store.close()
    state["_set_last_frame"](frame)
    return frame


def tick_system(state):
    """
    Advance system by one logical tick.
    """
    ticks = state["_get_ticks"]()
    state["_set_ticks"](ticks + 1)
    return ticks + 1