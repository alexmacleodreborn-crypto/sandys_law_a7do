"""
Debug View Utilities for A7DO
=============================

Pure visibility.
No mutation.
Safe to use at any phase.
"""

def print_world(world):
    a = world.agent
    print(
        f"World | "
        f"pos=({a.x},{a.y}) "
        f"effort={a.effort:.2f} "
        f"contact={a.contact} "
        f"thermal={a.thermal:.2f} "
        f"pain={a.pain:.2f}"
    )


def print_lifecycle(lc, tick):
    print("\n" + "=" * 40)
    print(f"TICK: {tick}")
    print(f"Phase: {lc.phase.current}")
    print(f"Born: {lc.born}")

    try:
        frames_count = len(lc.frames.frames)
    except Exception:
        frames_count = "n/a"

    print(f"Frames: {frames_count}")

    coherence_val = getattr(lc.coherence, "value", None)
    print(f"Coherence: {coherence_val}")


def draw_world(world):
    w, h = world.cfg.width, world.cfg.height
    ax, ay = world.agent.x, world.agent.y

    print("\nWORLD MAP:")
    for y in range(h):
        row = ""
        for x in range(w):
            if x == ax and y == ay:
                row += " A "
            else:
                row += " . "
        print(row)
