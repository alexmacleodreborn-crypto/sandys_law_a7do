# streamlit_app.py
"""
A7DO + Sandy’s Law
Streamlit Interface — Experiment Comparison Mode
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def run():
    # --------------------------------------------------
    # Lazy imports
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Persist system + experiments
    # --------------------------------------------------
    if "system_bundle" not in st.session_state:
        system, snapshot, state = build_system()
        st.session_state.system_bundle = {
            "snapshot": snapshot,
            "state": state,
            "experiments": {},  # name → result
        }

    bundle = st.session_state.system_bundle
    snapshot = bundle["snapshot"]
    state = bundle["state"]
    experiments = bundle["experiments"]

    # --------------------------------------------------
    # Page setup
    # --------------------------------------------------
    st.set_page_config(
        page_title="A7DO — Sandy’s Law Comparison",
        layout="wide",
    )
    st.title("A7DO — Sandy’s Law Experiment Comparison")

    # --------------------------------------------------
    # Sidebar: experiments
    # --------------------------------------------------
    st.sidebar.header("Run Experiments")

    if st.sidebar.button("▶ Stable Structure"):
        experiments["Stable"] = run_experiment(
            name="Stable",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=stable_pattern(),
        )

    if st.sidebar.button("▶ Fragmenting Structure"):
        experiments["Fragmenting"] = run_experiment(
            name="Fragmenting",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=fragmenting_pattern(),
        )

    if st.sidebar.button("▶ Overload Structure"):
        experiments["Overload"] = run_experiment(
            name="Overload",
            open_frame=lambda: inject_demo_frame(state),
            add_fragment=lambda k: add_fragment_by_kind(state, k),
            close_frame=lambda: close_frame(state),
            tick=lambda: tick_system(state),
            snapshot=snapshot,
            pattern=overload_pattern(),
        )

    if st.sidebar.button("🧹 Clear Experiments"):
        experiments.clear()

    # --------------------------------------------------
    # Snapshot overview
    # --------------------------------------------------
    data = snapshot()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("System State")
        st.json(
            {
                "roles": data["roles"],
                "ticks": data["ticks"],
                "active_frame": (
                    {
                        "domain": data["active_frame"].domain,
                        "label": data["active_frame"].label,
                        "fragments": len(data["active_frame"].fragments),
                    }
                    if data["active_frame"]
                    else None
                ),
            }
        )

    with col2:
        st.subheader("Regulation")
        st.json(data["regulation"])

    # --------------------------------------------------
    # Comparison plots
    # --------------------------------------------------
    if experiments:
        st.subheader("Metric Comparison Across Experiments")

        fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)

        for name, exp in experiments.items():
            rows = []
            for step in exp["history"]:
                rows.append(
                    {
                        "Tick": step["ticks"],
                        "Z": step["metrics"]["Z"],
                        "Coherence": step["metrics"]["Coherence"],
                        "Stability": step["metrics"]["Stability"],
                    }
                )
            df = pd.DataFrame(rows)

            axes[0].plot(df["Tick"], df["Z"], label=name)
            axes[1].plot(df["Tick"], df["Coherence"], label=name)
            axes[2].plot(df["Tick"], df["Stability"], label=name)

        axes[0].set_ylabel("Z (Fragmentation)")
        axes[1].set_ylabel("Coherence")
        axes[2].set_ylabel("Stability")
        axes[2].set_xlabel("Tick")

        for ax in axes:
            ax.set_ylim(0.0, 1.05)
            ax.grid(True)
            ax.legend()

        st.pyplot(fig)

    # --------------------------------------------------
    # Experiment summaries
    # --------------------------------------------------
    if experiments:
        st.subheader("Final States")

        for name, exp in experiments.items():
            with st.expander(name):
                st.json(
                    {
                        "metrics": exp["final"]["metrics"],
                        "regulation": exp["final"]["regulation"],
                    }
                )


if __name__ == "__main__":
    run()