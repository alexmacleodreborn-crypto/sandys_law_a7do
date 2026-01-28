from bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM
    """

    # ------------------------------------------------
    # TIME (single authority)
    # ------------------------------------------------
    state["ticks"] += 1

    # ------------------------------------------------
    # WOMB (prebirth environment)
    # ------------------------------------------------
    womb = state["womb_engine"]
    womb_state = womb.step()
    state["last_womb_state"] = womb_state

    # ------------------------------------------------
    # SCUTTLING (embodied growth)
    # ------------------------------------------------
    scuttling = state["scuttling_engine"]
    scuttling.step()

    # ------------------------------------------------
    # STRUCTURAL METRICS
    # ------------------------------------------------
    state["last_coherence"] = womb_state.rhythmic_stability
    state["structural_load"] = womb_state.ambient_load
    state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

    # ------------------------------------------------
    # BIRTH EVALUATION (ONCE)
    # ------------------------------------------------
    if state["birth_state"] is None:
        state["birth_state"] = state["birth_evaluator"].evaluate(
            tick=state["ticks"],
            metrics={
                "Stability": state["last_coherence"],
                "Load": state["structural_load"],
                "Z": state["last_fragmentation"],
            }
        )


class TickEngine:
    """
    Thin adapter around the canonical step_tick().

    This exists ONLY to provide a stable object interface
    for LifeCycle and visualization layers.
    """

    def __init__(self, state: dict | None = None):
        # IMPORTANT:
        # system_snapshot() returns a READ-ONLY VIEW
        # We must build the real mutable system state.
        if state is None:
            _, state = _build_state()
        self.state = state

    def tick(self) -> None:
        step_tick(self.state)

    def snapshot(self) -> dict:
        return system_snapshot(self.state)


# ------------------------------------------------
# Internal helper (avoids circular imports)
# ------------------------------------------------

def _build_state():
    """
    Local import to avoid circular dependency:
    tick_engine -> bootstrap -> tick_engine
    """
    from bootstrap import build_system
    return build_system()