# sandys_law_a7do/interfaces/chat/observer.py

from __future__ import annotations
from typing import Callable, Dict, Any, List


def render_chat_observer(snapshot: Callable[[], Dict[str, Any]]) -> str:
    """
    Read-only observer of A7DO system state.

    Rules:
    - Uses snapshot() ONLY
    - No state access
    - No decisions
    - No memory writes
    - No future planning
    """

    data = snapshot()

    ticks = data.get("ticks", 0)
    metrics = data.get("metrics", {})
    gates = data.get("gates", {})
    memory_count = data.get("memory_count", 0)

    Z = metrics.get("Z", 0.0)
    coherence = metrics.get("Coherence", 0.0)
    stability = metrics.get("Stability", 0.0)
    load = metrics.get("Load", 0.0)

    lines: List[str] = []

    # -------------------------------------------------
    # CORE STATE DESCRIPTION
    # -------------------------------------------------
    lines.append(
        f"Tick {ticks}: "
        f"Coherence={coherence:.2f}, "
        f"Stability={stability:.2f}, "
        f"Fragmentation={Z:.2f}, "
        f"Load={load:.2f}"
    )

    # -------------------------------------------------
    # FRAME STATUS
    # -------------------------------------------------
    active_frame = data.get("active_frame")
    if active_frame:
        lines.append(
            f"Active frame: {active_frame.domain}:{active_frame.label}"
        )
    else:
        lines.append("No active frame.")

    # -------------------------------------------------
    # GATES
    # -------------------------------------------------
    if gates:
        closed = [
            name for name, info in gates.items()
            if info.get("open") is False
        ]

        if closed:
            lines.append(
                "Restricted by gates: " + ", ".join(closed)
            )
        else:
            lines.append("No gates currently restricting progression.")
    else:
        lines.append("Gate data unavailable.")

    # -------------------------------------------------
    # MEMORY
    # -------------------------------------------------
    lines.append(f"Stored episodes: {memory_count}")

    # -------------------------------------------------
    # PREDICTION ERROR (IF PRESENT)
    # -------------------------------------------------
    if "prediction_error" in data:
        pe = data.get("prediction_error", 0.0)
        lines.append(f"Prediction error: {pe:.2f}")

    return "\n".join(lines)