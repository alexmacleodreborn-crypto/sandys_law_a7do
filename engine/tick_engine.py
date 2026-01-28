from bootstrap import system_snapshot


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM

    Responsibilities:
    - Advance time
    - Run womb physics ONLY pre-birth
    - Accumulate gestation criteria
    - Record developmental growth trace
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
    # PRE-BIRTH: WOMB + GESTATION + DEVELOPMENT TRACE
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

        # ------------------------------------------------
        # DEVELOPMENT TRACE (VISUALISATION ONLY)
        # ------------------------------------------------
        trace = state["development_trace"]

        trace["ticks"].append(state["ticks"])
        trace["heartbeat"].append(womb_state.heartbeat_rate)
        trace["ambient_load"].append(womb_state.ambient_load)
        trace["stability"].append(womb_state.rhythmic_stability)

        # Proto-brain coherence (capacity only, no semantics)
        trace["brain_coherence"].append(
            womb_state.rhythmic_stability
            * min(1.0, state["ticks"] / 100.0)
        )

        # Body growth precedes limbs
        trace["body_growth"].append(
            min(1.0, state["ticks"] / criteria.MIN_EXPOSURE_TIME)
        )

        trace["limb_growth"].append(
            max(0.0, (state["ticks"] - 20) / criteria.MIN_EXPOSURE_TIME)
        )

        # ---- Birth readiness & transition ----
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

            # 🔒 FREEZE WOMB ENGINE
            state["womb_engine"].womb_active = False

            # 🔒 FREEZE LAST WOMB SNAPSHOT (UI CONSISTENCY)
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
    scuttling = state["scuttling_engine"]
    scuttling.step()


class TickEngine:
    """
    Thin adapter around the canonical step_tick().

    Exists only to provide a stable interface
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