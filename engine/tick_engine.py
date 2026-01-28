from bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM

    Responsibilities:
    - Advance time
    - Run womb physics ONLY pre-birth
    - Accumulate gestation criteria
    - Delegate embodiment growth computation
    - Execute birth transition exactly once
    - Freeze womb engine AND womb snapshot after birth
    - Evaluate gates post-birth
    - Run scuttling continuously
    """

    # ------------------------------------------------
    # TIME (canonical)
    # ------------------------------------------------
    state["ticks"] += 1

    # ------------------------------------------------
    # PRE-BIRTH: WOMB + GESTATION
    # ------------------------------------------------
    if state["birth_state"] is None:
        womb = state["womb_engine"]
        womb_state = womb.step()
        state["last_womb_state"] = womb_state

        # Structural metrics
        state["last_coherence"] = womb_state.rhythmic_stability
        state["structural_load"] = womb_state.ambient_load
        state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

        # Gestation accumulation
        criteria = state["birth_criteria"]
        criteria.update(
            dt=1.0,
            stability=womb_state.rhythmic_stability,
            ambient_load=womb_state.ambient_load,
        )

        # ------------------------------------------------
        # EMBODIMENT GROWTH (DELEGATED)
        # ------------------------------------------------
        growth = state["embodiment_growth"].compute(
            tick=state["ticks"],
            stability=womb_state.rhythmic_stability,
            exposure_time=criteria._time_exposed,
            min_exposure=criteria.MIN_EXPOSURE_TIME,
        )

        trace = state["development_trace"]
        trace["ticks"].append(state["ticks"])
        trace["heartbeat"].append(womb_state.heartbeat_rate)
        trace["ambient_load"].append(womb_state.ambient_load)
        trace["stability"].append(womb_state.rhythmic_stability)
        trace["brain_coherence"].append(growth["brain_coherence"])
        trace["body_growth"].append(growth["body_growth"])
        trace["limb_growth"].append(growth["limb_growth"])

        # ------------------------------------------------
        # Birth readiness & transition
        # ------------------------------------------------
        readiness = criteria.evaluate()
        transition = state["birth_transition"].attempt_transition(
            readiness=readiness,
            state=state,
        )

        if transition.transitioned:
            from genesis.birth_state import BirthState

            state["birth_state"] = BirthState(
                born=True,
                reason=readiness.reason,
                tick=state["ticks"],
            )

            # Freeze womb engine
            state["womb_engine"].womb_active = False

            # Freeze last womb snapshot
            if state.get("last_womb_state") is not None:
                state["last_womb_state"].womb_active = False

    # ------------------------------------------------
    # POST-BIRTH: GATE EVALUATION
    # ------------------------------------------------
    if state["birth_state"] is not None:
        gate_engine = state["gate_engine"]
        gate_engine.evaluate(
            coherence=state["last_coherence"],
            fragmentation=state["last_fragmentation"],
            stability=state["last_coherence"] * (1.0 - state["structural_load"]),
            load=state["structural_load"],
        )

    # ------------------------------------------------
    # SCUTTLING (ALWAYS RUNS)
    # ------------------------------------------------
    state["scuttling_engine"].step()


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