# streamlit_app.py
"""
A7DO + Sandy's Law
Streamlit Interface with Experiment Mode
"""

import streamlit as st


def run():
    # Lazy imports
    from bootstrap import (
        build_system,
        inject_demo_frame,
        add_fragment,
        add_fragment_by_kind,
        close_frame,
        tick_system,
    )
    from experiments import (
        run_experiment,
        stable_pattern,
        fragmenting_pattern,
        overload_pattern,
    )

    # Persist system
    if "system_bundle" not in st.session_state:
        system, snapshot, state = build_system()
        st.session_state.system_bundle = {
            "snapshot": snapshot,
            "state": state,
            "experiment": None,
        }

    bundle = st.session_state.system_bundle
    snapshot = bundle["snapshot"]
    state = bundle["state"]

    st.set_page_config(page_title="A7DO Experiment Mode", layout="wide")
    st.title("A7DO — Sandy’s Law Experiment Mode")

    # --------------------------------------------------
    # SIDEBAR: EXPERIMENTS
    # --------------------------------------------------
    st.sidebar.header("Experiments")

    if st.sidebar.button("▶ Stable Structure"):
        bundle["experiment"] = run_experiment(
            name="Stable",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=stable_pattern(),
        )

    if st.sidebar.button("▶ Fragmenting Structure"):
        bundle["experiment"] = run_experiment(
            name="Fragmenting",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=fragmenting_pattern(),
        )

    if st.sidebar.button("▶ Overload Structure"):
        bundle["experiment"] = run_experiment(
            name="Overload",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=overload_pattern(),
        )

    # --------------------------------------------------
    # DISPLAY
    # --------------------------------------------------
    data = snapshot()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Current Metrics")
        for k, v in data["metrics"].items():
            st.progress(min(1.0, float(v)))
            st.caption(f"{k}: {float(v):.3f}")

    with col2:
        st.subheader("Regulation")
        st.json(data["regulation"])

    # --------------------------------------------------
    # EXPERIMENT RESULTS
    # --------------------------------------------------
    exp = bundle.get("experiment")
    if exp:
        st.subheader(f"Experiment Result: {exp['name']}")

        st.write("Final State")
        st.json(
            {
                "metrics": exp["final"]["metrics"],
                "regulation": exp["final"]["regulation"],
            }
        )

        st.write("Timeline")
        for step in exp["history"]:
            st.write(
                f"Tick {step['ticks']} → "
                f"Z={step['metrics']['Z']:.2f}, "
                f"Coherence={step['metrics']['Coherence']:.2f}, "
                f"Decision={step['regulation']}"
            )


if __name__ == "__main__":
    run()