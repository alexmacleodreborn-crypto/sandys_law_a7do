# experiments.py
"""
Sandy's Law — Experiment Mode
Deterministic structural experiments
"""

from typing import List, Dict


def run_experiment(
    *,
    name: str,
    open_frame,
    add_fragment,
    close_frame,
    tick,
    snapshot,
    pattern: List[str],
) -> Dict:
    """
    Runs a structural experiment.

    pattern: list of fragment kinds injected sequentially
    """

    history = []

    # Open frame
    open_frame()

    for kind in pattern:
        add_fragment(kind)
        tick()
        snap = snapshot()
        history.append(
            {
                "ticks": snap["ticks"],
                "metrics": snap["metrics"],
                "regulation": snap["regulation"]["decision"],
            }
        )

    # Close frame
    close_frame()
    final = snapshot()

    return {
        "name": name,
        "history": history,
        "final": final,
    }


# -----------------------------
# PREDEFINED EXPERIMENTS
# -----------------------------

def stable_pattern(n=6):
    # repeated same fragment → coherence dominates
    return ["demo"] * n


def fragmenting_pattern():
    # many unique fragments → fragmentation rises
    return ["a", "b", "c", "d", "e", "f"]


def overload_pattern():
    # burst injection → pressure proxy
    return ["x"] * 12