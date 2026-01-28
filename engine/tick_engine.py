from __future__ import annotations

from bootstrap import system_snapshot
from embodiment.anatomy import grow_anatomy
from world.world_state import WorldEventType


# ============================================================
# CANONICAL TICK
# ============================================================

def step_tick(state: dict) -> None:
    """
    THE ONLY CLOCK IN THE SYSTEM

    Doctrine:
    - Deterministic
    - Single causal step
    - No skipped phases
    """

    # =================================================
    # TIME
    # =================================================
    state["ticks"] += 1

    # =================================================
    # PRE-BIRTH — GESTATION ONLY
    # =================================================
    if state["birth_state"] is None:

        # --- Womb physics ---
        womb = state["womb_engine"]
        womb_state = womb.step()
        state["last_womb_state"] = womb_state

        # --- Umbilical buffering ---
        umb = state["umbilical_link"]
        umb_state = umb.step(womb_active=womb_state.womb_active)
        state["last_umbilical_state"] = umb_state

        # --- Structural metrics ---
        state["last_coherence"] = womb_state.rhythmic_stability
        state["structural_load"] = (
            womb_state.ambient_load * (1.0 - umb_state.load_transfer * 0.5)
        )
        state["last_fragmentation"] = 1.0 - womb_state.rhythmic_stability

        # --- Gestation criteria ---
        criteria = state["birth_criteria"]
        criteria.update(
            dt=1.0,
            stability=womb_state.rhythmic_stability,
            ambient_load=womb_state.ambient_load,
        )

        # --- Physical anatomy growth ---
        grow_anatomy(
            anatomy=state["anatomy"],
            stability=womb_state.rhythmic_stability,
        )

        # --- Observer trace (visual only) ---
        trace = state["development_trace"]
        trace["ticks"].append(state["ticks"])
        trace["heartbeat"].append(womb_state.heartbeat_rate)
        trace["ambient_load"].append(womb_state.ambient_load)
        trace["stability"].append(womb_state.rhythmic_stability)
        trace["brain_coherence"].append(state["last_coherence"])
        trace["body_growth"].append(
            sum(r["growth"] for r in state["anatomy"].values()) / len(state["anatomy"])
        )
        trace["limb_growth"].append(
            (
                state["anatomy"]["left_arm"]["growth"]
                + state["anatomy"]["right_arm"]["growth"]
                + state["anatomy"]["left_leg"]["growth"]
                + state["anatomy"]["right_leg"]["growth"]
            ) / 4
        )
        trace["umbilical_load"].append(umb_state.load_transfer)
        trace["rhythmic_coupling"].append(umb_state.rhythmic_coupling)

        # --- Birth transition ---
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

            # Freeze womb systems
            womb_state.womb_active = False
            umb_state.active = False

    # =================================================
    # POST-BIRTH — WORLD + PROTO-PERCEPTION
    # =================================================
    if state["birth_state"] is not None:

        # --- World step (no voluntary action yet) ---
        state["world_runner"].step(action=None)

        # --- Sense world (STRICTLY gated) ---
        world_events = state["sensor_suite"].sense()

        # --- Sensory readiness ramp ---
        state["sensory_readiness"].step(born=True)

        # --- Developmental noise only ---
        raw_input = {
            "vision": 0.05,   # light / shadow
            "sound": 0.1,    # muffled noise
            "touch": 0.05,   # diffuse contact
        }

        packets = state["sensory_wall"].filter(
            raw_input=raw_input,
            anatomy=state["anatomy"],
            sensory_levels=state["sensory_readiness"].snapshot(),
        )

        state["last_sensory_packets"] = packets

        # --- Frames (no meaning) ---
        state["frames"].observe_sensory(packets)

        # --- Square (repetition only) ---
        state["square"].observe_packets(packets)

        # --- Gates evaluate AFTER perception ---
        state["gate_engine"].evaluate(
            coherence=state["last_coherence"],
            fragmentation=state["last_fragmentation"],
            stability=state["last_coherence"] * (1.0 - state["structural_load"]),
            load=state["structural_load"],
        )

    # =================================================
    # SCUTTLING (ALWAYS RUNS)
    # =================================================
    state["scuttling_engine"].step()


# ============================================================
# ENGINE ADAPTER
# ============================================================

class TickEngine:
    """
    Thin adapter around step_tick.
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