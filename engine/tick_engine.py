from bootstrap import system_snapshot
from embodiment.anatomy import grow_anatomy


def step_tick(state: dict) -> None:

    state["ticks"] += 1

    # =================================================
    # PRE-BIRTH
    # =================================================
    if state["birth_state"] is None:
        womb = state["womb_engine"]
        womb_state = womb.step()
        state["last_womb_state"] = womb_state

        umb = state["umbilical_link"]
        umb_state = umb.step(womb_active=womb_state.womb_active)
        state["last_umbilical_state"] = umb_state

        state["last_coherence"] = womb_state.rhythmic_stability
        state["structural_load"] = womb_state.ambient_load
        state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

        criteria = state["birth_criteria"]
        criteria.update(
            dt=1.0,
            stability=womb_state.rhythmic_stability,
            ambient_load=womb_state.ambient_load,
        )

        grow_anatomy(
            anatomy=state["anatomy"],
            stability=womb_state.rhythmic_stability,
        )

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

    # =================================================
    # POST-BIRTH — SENSORY WALL → FRAMES
    # =================================================
    if state["birth_state"] is not None:
        state["sensory_readiness"].step(born=True)

        raw_input = {
            "vision": 0.5,
            "sound": 0.4,
            "touch": 0.3,
        }

        packets = state["sensory_wall"].filter(
            raw_input=raw_input,
            anatomy=state["anatomy"],
            sensory_levels=state["sensory_readiness"].snapshot(),
        )

        state["last_sensory_packets"] = packets

        state["frames"].observe_sensory(packets)

        state["gate_engine"].evaluate(
            coherence=state["last_coherence"],
            fragmentation=state["last_fragmentation"],
            stability=state["last_coherence"]
            * (1.0 - state["structural_load"]),
            load=state["structural_load"],
        )

    state["scuttling_engine"].step()


class TickEngine:
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