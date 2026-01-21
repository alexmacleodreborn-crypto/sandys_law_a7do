# sandys_law_a7do/engine/tick_engine.py

"""
Tick Engine — v1.1 (Perception Wired)

Implements:
- Tick progression
- Perceptual variation injection
- Metric evolution (NO learning here)

Learning remains episode-based (frame close).
"""

from sandys_law_a7do.mind.perception import perceive
from sandys_law_a7do.frames.fragment import Fragment


def step_tick(state: dict, snapshot):
    """
    Single system tick.

    Rules:
    - Advances time
    - Injects perceptual variation
    - Does NOT write memory
    - Does NOT close frames
    """

    frames = state["frames"]
    active = frames.active

    # -----------------------------
    # ADVANCE TICK
    # -----------------------------
    state["ticks"] += 1

    # -----------------------------
    # PERCEPTION → STRUCTURE
    # -----------------------------
    if active:
        percepts = perceive(state)

        for p in percepts:
            # Safety: perception must only add fragments
            if isinstance(p, Fragment):
                frames.add_fragment(p)

    # -----------------------------
    # SNAPSHOT ONLY (NO SIDE EFFECTS)
    # -----------------------------
    snapshot()