# sandys_law_a7do/streamlit_app.py
"""
Streamlit entry point (launcher)

This file exists ONLY to launch the real dashboard located at:
interfaces/dashboard/streamlit_app.py
"""

from interfaces.dashboard.streamlit_app import main
from bootstrap import build_system


def run():
    _, snapshot, _ = build_system()
    main(snapshot)


if __name__ == "__main__":
    run()