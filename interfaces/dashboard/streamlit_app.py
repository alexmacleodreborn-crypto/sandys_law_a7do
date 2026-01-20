# streamlit_app.py
"""
Streamlit Cloud entry point (SAFE).
"""

import streamlit as st


def run():
    # Lazy imports ONLY after Streamlit is ready
    from bootstrap import build_system
    from interfaces.dashboard.streamlit_app import main as dashboard_main

    _, snapshot = build_system()
    dashboard_main(snapshot)


if __name__ == "__main__":
    run()