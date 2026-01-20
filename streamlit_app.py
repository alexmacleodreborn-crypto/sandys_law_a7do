# streamlit_app.py

import streamlit as st


def run():
    from bootstrap import build_system, inject_demo_frame, tick_system
    from interfaces.dashboard.streamlit_app import main as dashboard_main

    system, snapshot, state = build_system()

    st.sidebar.header("Controls")

    if st.sidebar.button("➕ Inject Demo Frame"):
        inject_demo_frame(state)

    if st.sidebar.button("▶ Tick"):
        tick_system(state)

    dashboard_main(snapshot)


if __name__ == "__main__":
    run()