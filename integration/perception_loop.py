# sandys_law_a7do/integration/perception_loop.py

"""
Embodied Perception Loop (Phase 4)

Produces STRUCTURE, not thoughts.
Safe, bounded, non-learning.
"""

import random
from sandys_law_a7do.frames.fragment import Fragment


def perceive_and_act(state):
    """
    Minimal embodied perception.

    Returns a list of Fragments to inject.
    """
    outputs = []

    # Baseline environment (always present)
    outputs.append(Fragment(kind="env:baseline"))

    # Occasional novelty
    if random.random() < 0.3:
        outputs.append(Fragment(kind="env:novel"))

    # Rare pressure spike
    if random.random() < 0.1:
        outputs.append(Fragment(kind="env:pressure"))

    return outputs