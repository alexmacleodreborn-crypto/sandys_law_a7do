# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (FINAL, FACTORY-SAFE)

Rules:
- Bootstrap owns state
- UI may request actions only
- NO Streamlit imports
- NO direct Frame() construction
"""

# =========================================================
# CORE IMPORTS
# =========================================================

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
    """
    Build system once.
    Returns:
        system_manager
        snapshot_provider()
        control_state
    """

    frames_store = FrameStore()
    memory = StructuralMemory()
    embodiment_ledger = EmbodimentLedger()
    boundaries = BoundaryState()
    preferences = PreferenceEngine()

    ticks = 0

    # -----------------------------
    # Roles
    # -----------------------------
    system = SystemManager()
    sled = SLEDInterface()
    system.register(sled)

    # -----------------------------------------------------
    # FRAME ACCESS NORMALIZER
    # -----------------------------------------------------
    def _get_active_frames():
        """
        Always return a LIST of frames.
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
    # SNAPSHOT (READ-ONLY)
    # -----------------------------------------------------
    def snapshot():
        nonlocal ticks

        active_frames = _get_active_frames()

        # --- Perception ---
        fragments = []
        for f in active_frames:
            for frag in getattr(f, "fragments", []):
                fragments.append(
                    {"action": getattr(frag, "kind", "unknown")}
                )

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
            "frames": active_frames,
            "metrics": metrics,
            "regulation": {
                "decision": regulation.decision,
                "reason": regulation.reason,
            },
        }

    # -----------------------------------------------------
    # CONTROL STATE
    # -----------------------------------------------------
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
# CONTROLLED ACTIONS (UI CALLABLE)
# =========================================================

def inject_demo_frame(state):
    """
    Create a frame using FrameStore factory
    and inject a demo fragment.
    """
    frames_store = state["frames_store"]

    # --- Create frame via FrameStore (NO direct Frame()) ---
    frame = None
    for name in ("create_frame", "new_frame", "open_frame", "open", "start_frame"):
        fn = getattr(frames_store, name, None)
        if callable(fn):
            frame = fn()
            break

    if frame is None:
        # Cannot create frame safely
        return None

    # --- Add fragment using frame API ---
    frag = Fragment(kind="demo", payload={"source": "bootstrap"})

    if hasattr(frame, "add"):
        frame.add(frag)
    elif hasattr(frame, "add_fragment"):
        frame.add_fragment("demo", {"source": "bootstrap"})

    return frame


def add_fragment_to_last_frame(state):
    """
    Add fragment to most recent frame.
    """
    frames_store = state["frames_store"]

    frames = None
    if hasattr(frames_store, "frames") and isinstance(frames_store.frames, list):
        frames = frames_store.frames
    elif hasattr(frames_store, "store") and isinstance(frames_store.store, list):
        frames = frames_store.store

    if not frames:
        return None

    frame = frames[-1]
    frag = Fragment(kind="demo", payload={"source": "bootstrap"})

    if hasattr(frame, "add"):
        frame.add(frag)
    elif hasattr(frame, "add_fragment"):
        frame.add_fragment("demo", {"source": "bootstrap"})

    return frame


def tick_system(state):
    """
    Advance system by one logical tick.
    """
    ticks = state["ticks"]()
    state["_set_ticks"](ticks + 1)
    return ticks + 1