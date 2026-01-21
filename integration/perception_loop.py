# sandys_law_a7do/integration/perception_loop.py

import random
from sandys_law_a7do.frames.fragment import Fragment

# --------------------------------------------------
# Minimal embodied perception loop
# --------------------------------------------------

def perceive_and_act(state):
    """
    Generate structural fragments from a minimal 'world'.
    No semantics. No rewards. Just variation.
    """

    # Simulated sensory variation (placeholder for real world)
    sensory_load = random.choice(["low", "med", "high"])
    novelty = random.choice([0, 1])

    fragments = []

    # Load fragment
    fragments.append(
        Fragment(kind=f"load:{sensory_load}")
    )

    # Novelty fragment (sometimes)
    if novelty:
        fragments.append(
            Fragment(kind="novel")
        )

    return fragments