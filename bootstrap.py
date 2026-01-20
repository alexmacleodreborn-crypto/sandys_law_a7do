# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (FINAL, NORMALIZED)
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

    system = SystemManager()
    sled = SLEDInterface()
    system.register(sled)

    # -----------------------------------------------------
    # FRAME NORMALIZER (THE KEY FIX)
    # -----------------------------------------------------
    def _get_active_frames():
        """
        Always return a LIST of frames.
        Never None. Never non-iterable.
        """
        candidates = [
            getattr(frames_store, "frames", None),
            getattr(frames_store, "_frames", None),
            getattr(frames_store, "store", None),
            getattr(frames_store, "active", None),
        ]

        for c in candidates:
            if isinstance(c, list):
                return c

        # Try callable accessor
        for name in ("all", "get_all", "list"):
            fn = getattr(frames_store, name, None)
            if callable(fn):
                try:
                    result = fn()
                    if isinstance(result, list):
                        return result
                except Exception:
                    pass

        return []  # FINAL GUARANTEE

    # -----------------------------------------------------
    # SNAPSHOT
    # -----------------------------------------------------
    def snapshot():
        nonlocal ticks

        active_frames = _get_active_frames()

        # --- Perception ---
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
        "_set_ticks": lambda v: None,
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
    frames_store = state["frames_store"]

    frame = Frame()
    frag = Fragment(kind="demo", payload={"source": "bootstrap"})
    frame.add(frag)

    if hasattr(frames_store, "add"):
        frames_store.add(frame)
    elif hasattr(frames_store, "frames") and isinstance(frames_store.frames, list):
        frames_store.frames.append(frame)

    return frame


def add_fragment_to_last_frame(state):
    frames_store = state["frames_store"]

    frames = getattr(frames_store, "frames", [])
    if not isinstance(frames, list) or not frames:
        return None

    frag = Fragment(kind="demo", payload={"source": "bootstrap"})
    frames[-1].add(frag)
    return frag


def tick_system(state):
    ticks = state["ticks"]()
    state["_set_ticks"](ticks + 1)
    return ticks + 1