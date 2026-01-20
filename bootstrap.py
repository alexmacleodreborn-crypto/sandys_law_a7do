# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap (authoritative)

Rules:
- NO Streamlit imports
- NO UI imports
- Owns all mutable state
- UI may only call exposed functions
"""

# =========================================================
# CORE IMPORTS
# =========================================================

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
    """
    Build the system ONCE.
    Returns:
        system_manager
        snapshot_provider (callable)
        control_state (dict)
    """

    # -----------------------------
    # Core state
    # -----------------------------
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

    # -----------------------------
    # SNAPSHOT (READ-ONLY)
    # -----------------------------
    def snapshot():
        nonlocal ticks

        active_frames = frames_store.frames

        # --- Perception ---
        fragments = []
        for f in active_frames:
            for frag in f.fragments:
                fragments.append(
                    {"action": frag.kind}
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

    # -----------------------------
    # CONTROL STATE (MUTABLE)
    # -----------------------------
    control_state = {
        "frames_store": frames_store,
        "boundaries": boundaries,
        "memory": memory,
        "preferences": preferences,
        "ticks": lambda: ticks,
        "_set_ticks": lambda v: None,
    }

    # allow mutation safely
    def _set_ticks(v):
        nonlocal ticks
        ticks = v

    control_state["_set_ticks"] = _set_ticks

    return system, snapshot, control_state


# =========================================================
# CONTROLLED ACTIONS (CALLED BY UI)
# =========================================================

def inject_demo_frame(state):
    """
    Inject a demo frame with one fragment.
    """
    frames_store = state["frames_store"]

    frame = Frame()
    frag = Fragment(kind="demo", payload={"source": "bootstrap"})
    frame.add(frag)

    frames_store.add(frame)
    return frame


def add_fragment_to_last_frame(state):
    """
    Add a fragment to the most recent frame.
    """
    frames_store = state["frames_store"]
    if not frames_store.frames:
        return None

    frag = Fragment(kind="demo", payload={"source": "bootstrap"})
    frames_store.frames[-1].add(frag)
    return frag


def tick_system(state):
    """
    Advance system by one logical step.
    """
    ticks = state["ticks"]()
    state["_set_ticks"](ticks + 1)
    return ticks + 1