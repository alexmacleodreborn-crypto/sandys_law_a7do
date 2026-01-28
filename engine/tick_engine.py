# =================================================
# POST-BIRTH
# =================================================
if state["birth_state"] is not None:

    # Step world (no voluntary action yet)
    world_events = state["world_runner"].step(action=None)

    # Sense world → observations
    observations = state["sensor_suite"].sense()

    # Sensory readiness ramp
    state["sensory_readiness"].step(born=True)

    # Raw sensory noise (developmental)
    raw_input = {
        "vision": 0.05,
        "sound": 0.1,
        "touch": 0.05,
    }

    packets = state["sensory_wall"].filter(
        raw_input=raw_input,
        anatomy=state["anatomy"],
        sensory_levels=state["sensory_readiness"].snapshot(),
    )

    state["last_sensory_packets"] = packets
    state["frames"].observe_sensory(packets)
    state["square"].observe_packets(packets)

    state["gate_engine"].evaluate(
        coherence=state["last_coherence"],
        fragmentation=state["last_fragmentation"],
        stability=state["last_coherence"] * (1.0 - state["structural_load"]),
        load=state["structural_load"],
    )