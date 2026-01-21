# sandys_law_a7do/integration/perception_loop.py
"""
Phase 4.1 — Minimal Perceptual Variation

Purpose:
- Introduce controlled structural diversity
- Allow Z to move without destabilising the system
- Preserve Sandy’s Law constraints
"""

import random
from sandys_law_a7do.frames.fragment import Fragment


def perceive_and_act(state):
    """
    Minimal embodied perception loop.

    Produces small structural variation only.
    No semantics, no reward, no goals.
    """

    fragments = []

    # --------------------------------------------------
    # Base environmental load (always present)
    # --------------------------------------------------
    load_level = random.choice(["low", "medium"])
    fragments.append(Fragment(kind=f"load:{load_level}"))

    # --------------------------------------------------
    # Occasional novelty (30% chance)
    # --------------------------------------------------
    if random.random() < 0.3:
        fragments.append(Fragment(kind="novel"))

    # --------------------------------------------------
    # Rare pressure spike (10% chance)
    # --------------------------------------------------
    if random.random() < 0.1:
        fragments.append(Fragment(kind="pressure"))

    return fragments