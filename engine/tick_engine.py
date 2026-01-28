from bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM
    """

    # ------------------------------------------------
    # TIME
    # ------------------------------------------------
    state["ticks"] += 1

    # ------------------------------------------------
    # WOMB (prebirth physics)
    # ------------------------------------------------
    womb = state["womb_engine"]
    womb_state = womb.step()
    state["last_womb_state"] = womb_state

    # ------------------------------------------------
    # SCUTTLING (always runs, but muted pre-birth)
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
    # BIRTH CRITERIA UPDATE (GESTATION)
    # ------------------------------------------------
    criteria = state["birth_criteria"]
    criteria.update(
        dt=1.0,
        stability=womb_state.rhythmic_stability,
        ambient_load=womb_state.ambient_load,
    )

    # ------------------------------------------------
    # BIRTH TRANSITION (ONCE, GUARDED)
    # ------------------------------------------------
    if state["birth_state"] is None:
        readiness = criteria.evaluate()
        transition = state["birth_transition"].attempt_transition(
            readiness=readiness,
            state=state,
        )

        if transition.transitioned:
            from genesis.birth import BirthState
            state["birth_state"] = BirthState(
                born=True,
                reason=readiness.reason,
                tick=state["ticks"],
            )


class TickEngine:
    """
    Thin adapter around the canonical step_tick().
    """

    def __init__(self, state: dict | None = None):
        if state is None:
            _, state = _build_state()
        self.state = state

    def tick(self) -> None:
        step_tick(self.state)

    def snapshot(self) -> dict:
        return system_snapshot(self.state)


def _build_state():
    from bootstrap import build_system
    return build_system()