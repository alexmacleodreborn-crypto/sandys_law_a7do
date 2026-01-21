# sandys_law_a7do/engine/tick_engine.py

"""
Tick Engine — v1.2

- Advances ticks
- Injects embodied perception
- NO memory writes
- NO cognition
"""

from sandys_law_a7do.integration.perception_loop import perceive_and_act
from sandys_law_a7do.frames.fragment import Fragment


def step_tick(state: dict, snapshot):
    frames = state["frames"]
    active = frames.active

    # -----------------------------
    # ADVANCE TIME
    # -----------------------------
    state["ticks"] += 1

    # -----------------------------
    # EMBODIED PERCEPTION
    # -----------------------------
    if active:
        percepts = perceive_and_act(state)

        for p in percepts:
            if isinstance(p, Fragment):
                frames.add_fragment(p)

    # -----------------------------
    # OBSERVE ONLY
    # -----------------------------
    snapshot()