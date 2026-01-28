# engine/tick_engine.py

from bootstrap import system_snapshot
from embodiment.anatomy import grow_anatomy


def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM

    Responsibilities:
    - Advance time
    - Run womb physics ONLY pre-birth
    - Maintain umbilical life support
    - Accumulate gestation criteria
    - Grow anatomical body
    - Execute birth transition exactly once
    - Freeze womb + umbilical at engine level
    - Ramp sensory readiness post-birth
    - Gate perception → frames
    - Run scuttling continuously
    """

    # =================================================
    # TIME
    # =================================================
    state["ticks"] += 1

    # =================================================
    # PRE-BIRTH (GESTATION)
    # =================================================
    if state["birth_state"] is None:
        # ---- Womb physics (ENGINE owns activity) ----
        womb_engine = state["womb_engine"]
        womb_state = womb_engine.step()
        state["last_womb_state"] = womb_state

        # ---- Umbilical life support ----
        umb_engine = state["umbilical_link"]
        umb_state = umb_engine.step(womb_active=womb_engine.active)
        state["last_umbilical_state"] = umb_state

        # ---- Structural metrics (umbilical buffers load) ----
        state["last_coherence"] = womb_state.rhythmic_stability
        state["structural_load"] = (
            womb_state.ambient_load * (1.0 - umb_state.load_transfer * 0.5)
        )
        state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

        # ---- Gestation criteria accumulation ----
        criteria = state["birth_criteria"]
        criteria.update(
            dt=1.0,
            stability=womb_state.rhythmic_stability,
            ambient_load=womb_state.ambient_load,
        )

        # ---- Anatomical growth (BIOLOGICAL BODY) ----
        grow_anatomy(
            anatomy=state["anatomy"],
            stability=womb_state.rhythmic_stability,
        )

        # ---- Birth evaluation ----
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

            # 🔒 CRITICAL FIX: freeze ENGINES, not snapshots
            womb_engine.active = False
            umb_engine.active = False

    # =================================================
    # POST-BIRTH — SENSORY WALL → FRAMES
    # =================================================
    if state["birth_state"] is not None:
        # ---- Sensory readiness ramp ----
        state["sensory_readiness"].step(born=True)

        # ---- Environmental noise (NOT perception yet) ----
        raw_input = {
            "vision": 0.05,   # shadow/light only
            "sound": 0.10,    # muffled noise
            "touch": 0.05,    # diffuse contact
        }

        sensory_wall = state.get("sensory_wall")
        if sensory_wall:
            packets = sensory_wall.filter(
                raw_input=raw_input,
                anatomy=state["anatomy"],
                sensory_levels=state["sensory_readiness"].snapshot(),
            )

            state["last_sensory_packets"] = packets
            state["frames"].observe_sensory(packets)

        # ---- Gate evaluation AFTER perception ----
        state["gate_engine"].evaluate(
            coherence=state["last_coherence"],
            fragmentation=state["last_fragmentation"],
            stability=state["last_coherence"]
            * (1.0 - state["structural_load"]),
            load=state["structural_load"],
        )

    # =================================================
    # SCUTTLING (ALWAYS RUNS)
    # =================================================
    state["scuttling_engine"].step()


# =====================================================
# ENGINE WRAPPER
# =====================================================

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