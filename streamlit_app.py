# streamlit_app.py
"""
A7DO + Sandy’s Law
Streamlit Interface — Experiment Mode with Metric Plots
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt


def run():
    # --------------------------------------------------
    # Lazy imports (Streamlit-safe)
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
    # Persist system across reruns
    # --------------------------------------------------
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

    # --------------------------------------------------
    # Page setup
    # --------------------------------------------------
    st.set_page_config(page_title="A7DO — Sandy’s Law Experiments", layout="wide")
    st.title("A7DO — Sandy’s Law Experiment Mode")

    # --------------------------------------------------
    # Sidebar: manual controls
    # --------------------------------------------------
    st.sidebar.header("Manual Frame Controls")

    if st.sidebar.button("▶ Open Demo Frame"):
        inject_demo_frame(state)

    if st.sidebar.button("➕ Add Demo Fragment"):
        try:
            add_fragment(state)
        except RuntimeError as e:
            st.sidebar.warning(str(e))

    if st.sidebar.button("⏹ Close Frame"):
        close_frame(state)

    st.sidebar.divider()

    if st.sidebar.button("⏱ Tick"):
        tick_system(state)

    # --------------------------------------------------
    # Sidebar: experiments
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
    # Current metrics
    # --------------------------------------------------
    st.subheader("Current Metrics")
    for k, v in data["metrics"].items():
        st.progress(min(1.0, float(v)))
        st.caption(f"{k}: {float(v):.3f}")

    # --------------------------------------------------
    # Experiment results + plots
    # --------------------------------------------------
    exp = bundle.get("experiment")
    if exp:
        st.subheader(f"Experiment Result: {exp['name']}")

        # -----------------------------
        # Final state
        # -----------------------------
        st.write("Final State")
        st.json(
            {
                "metrics": exp["final"]["metrics"],
                "regulation": exp["final"]["regulation"],
            }
        )

        # -----------------------------
        # Build dataframe from history
        # -----------------------------
        rows = []
        for step in exp["history"]:
            rows.append(
                {
                    "Tick": step["ticks"],
                    "Z": step["metrics"]["Z"],
                    "Coherence": step["metrics"]["Coherence"],
                    "Stability": step["metrics"]["Stability"],
                    "Regulation": step["regulation"],
                }
            )

        df = pd.DataFrame(rows)

        # -----------------------------
        # Metric evolution plot
        # -----------------------------
        st.subheader("Metric Evolution")

        fig, ax = plt.subplots()
        ax.plot(df["Tick"], df["Z"], label="Z (Fragmentation)")
        ax.plot(df["Tick"], df["Coherence"], label="Coherence")
        ax.plot(df["Tick"], df["Stability"], label="Stability")

        ax.set_xlabel("Tick")
        ax.set_ylabel("Metric Value")
        ax.set_ylim(0.0, 1.05)
        ax.legend()
        ax.grid(True)

        st.pyplot(fig)

        # -----------------------------
        # Regulation timeline
        # -----------------------------
        st.subheader("Regulation Timeline")
        st.table(df[["Tick", "Regulation"]])


if __name__ == "__main__":
    run()