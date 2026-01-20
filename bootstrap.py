# bootstrap.py
"""
A7DO + Sandy's Law
System Bootstrap

This is the ONLY file allowed to wire subsystems together.
"""

# =========================================================
# CORE IMPORTS
# =========================================================

from roles.system_manager import SystemManager
from roles.sled_interface import SLEDInterface

from frames.store import FrameStore
from memory.structural_memory import StructuralMemory

from embodiment.ledger import EmbodimentLedger
from embodiment.boundaries import BoundaryState

from mind.preference import PreferenceEngine
from mind.perception import summarize_perception
from mind.coherence import compute_coherence
from mind.regulation import regulate

from accounting.metrics import metric_bundle

# Optional / UI
from interfaces.dashboard.streamlit_app import main as dashboard_main
from interfaces.chat.chat_cli import run_chat


# =========================================================
# SYSTEM CONSTRUCTION
# =========================================================

def build_system():
    """
    Construct and wire the full system.
    Returns (system_manager, snapshot_provider)
    """

    # --- Core state ---
    frames = FrameStore()
    memory = StructuralMemory()

    embodiment_ledger = EmbodimentLedger()
    boundaries = BoundaryState()

    preferences = PreferenceEngine()

    # --- Roles ---
    system = SystemManager()
    sled = SLEDInterface()

    system.register(sled)

    # -----------------------------------------------------
    # SNAPSHOT PROVIDER (READ-ONLY)
    # -----------------------------------------------------

    def snapshot():
        """
        Provides a safe, read-only snapshot for interfaces.
        """
        active_frames = frames.frames if hasattr(frames, "frames") else []

        # --- Perception summary ---
        fragments = []
        for f in active_frames:
            for frag in getattr(f, "fragments", []):
                fragments.append(
                    {
                        "action": getattr(frag, "kind", "unknown"),
                    }
                )

        percept = summarize_perception(fragments)

        coherence = compute_coherence(
            fragment_count=percept.fragment_count,
            unique_actions=percept.unique_actions,
            blocked_events=len(boundaries.__dict__.get("hard_pressure", []))
            if hasattr(boundaries, "__dict__")
            else 0,
        )

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
            "frames": active_frames,
            "metrics": metrics,
            "regulation": {
                "decision": regulation.decision,
                "reason": regulation.reason,
            },
        }

    return system, snapshot


# =========================================================
# ENTRY MODES
# =========================================================

def run_dashboard():
    _, snapshot = build_system()
    dashboard_main(snapshot)


def run_chat_cli():
    _, snapshot = build_system()
    run_chat(snapshot)


# =========================================================
# MAIN
# =========================================================

if __name__ == "__main__":
    import sys

    mode = sys.argv[1] if len(sys.argv) > 1 else "dashboard"

    if mode == "chat":
        run_chat_cli()
    else:
        run_dashboard()
