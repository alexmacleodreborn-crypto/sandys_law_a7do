from bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM

    Responsibilities:
    - Advance time
    - Run womb physics ONLY pre-birth
    - Accumulate gestation criteria
    - Run scuttling continuously
    - Execute birth transition exactly once
    """

    # ------------------------------------------------
    # TIME (canonical)
    # ------------------------------------------------
    state["ticks"] += 1

    # ------------------------------------------------
    # PRE-BIRTH ONLY: WOMB + GESTATION
    # ------------------------------------------------
    if state["birth_state"] is None:
        # ---- Womb physics ----
        womb = state["womb_engine"]
        womb_state = womb.step()
        state["last_womb_state"] = womb_state

        # ---- Structural metrics ----
        state["last_coherence"] = womb_state.rhythmic_stability
        state["structural_load"] = womb_state.ambient_load
        state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

        # ---- Gestation accumulation ----
        criteria = state["birth_criteria"]
        criteria.update(
            dt=1.0,
            stability=womb_state.rhythmic_stability,
            ambient_load=womb_state.ambient_load,
        )

        # ---- Birth transition check ----
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

    # ------------------------------------------------
    # SCUTTLING (always runs, pre & post birth)
    # ------------------------------------------------
    scuttling = state["scuttling_engine"]
    scuttling.step()


class TickEngine:
    """
    Thin adapter around the canonical step_tick().

    This class exists only to provide a stable interface
    for LifeCycle and visualization layers.
    """

    def __init__(self, state: dict | None = None):
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
    from bootstrap import build_system
    return build_system()