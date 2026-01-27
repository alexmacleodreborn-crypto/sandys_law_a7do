from sandys_law_a7do.bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM
    """

    # ------------------------------------------------
    # TIME
    # ------------------------------------------------
    state["tick"] += 1

    # ------------------------------------------------
    # WOMB (prebirth environment)
    # ------------------------------------------------
    womb = state["womb"]
    womb_state = womb.step()
    state["womb_state"] = womb_state

    # ------------------------------------------------
    # SCUTTLING (embodied growth)
    # ------------------------------------------------
    scuttling = state["scuttling"]
    scuttling.step()

    # ------------------------------------------------
    # STRUCTURAL METRICS (simple + conservative)
    # ------------------------------------------------
    state["last_stability"] = womb_state.rhythmic_stability
    state["last_load"] = womb_state.ambient_load
    state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

    # ------------------------------------------------
    # BIRTH EVALUATION (ONCE)
    # ------------------------------------------------
    if state["birth_state"] is None:
        state["birth_state"] = state["birth_evaluator"].evaluate(
            tick=state["tick"],
            metrics={
                "Stability": state["last_stability"],
                "Load": state["last_load"],
                "Z": state["last_fragmentation"],
            }
        )