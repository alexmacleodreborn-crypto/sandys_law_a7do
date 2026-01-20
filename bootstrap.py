# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (FINAL, ARG-SAFE)
"""

from roles.system_manager import SystemManager
from roles.sled_interface import SLEDInterface

from frames.store import FrameStore
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

    system = SystemManager()
    sled = SLEDInterface()
    system.register(sled)

    # -----------------------------------------------------
    # FRAME NORMALIZER
    # -----------------------------------------------------
    def _get_active_frames():
        candidates = [
            getattr(frames_store, "frames", None),
            getattr(frames_store, "_frames", None),
            getattr(frames_store, "store", None),
            getattr(frames_store, "active", None),
        ]
        for c in candidates:
            if isinstance(c, list):
                return c

        for name in ("all", "get_all", "list"):
            fn = getattr(frames_store, name, None)
            if callable(fn):
                try:
                    result = fn()
                    if isinstance(result, list):
                        return result
                except Exception:
                    pass

        return []

    # -----------------------------------------------------
    # SNAPSHOT
    # -----------------------------------------------------
    def snapshot():
        nonlocal ticks

        active_frames = _get_active_frames()

        fragments = []
        for f in active_frames:
            for frag in getattr(f, "fragments", []):
                fragments.append({"action": getattr(frag, "kind", "unknown")})

        percept = summarize_perception(fragments)

        hard_pressure = getattr(boundaries, "hard_pressure", 0.0)
        blocked_events = int(hard_pressure * 10)

        coherence = compute_coherence(
            fragment_count=percept.fragment_count,
            unique_actions=percept.unique_actions,
            blocked_events=blocked_events,
        )

        regulation = regulate(
            coherence=coherence.coherence,
            fragmentation=coherence.fragmentation,
            block_rate=coherence.block_rate,
        )

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
            "frames": active_frames,
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
        "ticks": lambda: ticks,
        "_set_ticks": None,
    }

    def _set_ticks(v):
        nonlocal ticks
        ticks = v

    state["_set_ticks"] = _set_ticks

    return system, snapshot, state


# =========================================================
# CONTROLLED ACTIONS
# =========================================================

def inject_demo_frame(state):
    """
    Attempt to create a demo frame safely.
    If FrameStore requires arguments, exit cleanly.
    """
    frames_store = state["frames_store"]

    frame = None
    for name in ("create_frame", "new_frame", "open_frame", "open", "start_frame"):
        fn = getattr(frames_store, name, None)
        if callable(fn):
            try:
                frame = fn()
                break
            except TypeError:
                # Factory requires args → do nothing safely
                return None

    if frame is None:
        return None

    frag = Fragment(kind="demo", payload={"source": "bootstrap"})

    if hasattr(frame, "add"):
        frame.add(frag)
    elif hasattr(frame, "add_fragment"):
        frame.add_fragment("demo", {"source": "bootstrap"})

    return frame


def tick_system(state):
    ticks = state["ticks"]()
    state["_set_ticks"](ticks + 1)
    return ticks + 1