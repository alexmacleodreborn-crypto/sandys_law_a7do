# sandys_law_a7do/streamlit_app.py
"""
Streamlit entry point for A7DO

This file MUST import the package, not local files.
"""

import sys
from pathlib import Path

# --------------------------------------------------
# Ensure project root is on PYTHONPATH
# --------------------------------------------------
ROOT = Path(__file__).resolve().parent
if str(ROOT.parent) not in sys.path:
    sys.path.insert(0, str(ROOT.parent))

# --------------------------------------------------
# Import via package (CRITICAL)
# --------------------------------------------------
from sandys_law_a7do.bootstrap import build_system
from sandys_law_a7do.interfaces.dashboard.streamlit_app import main


def run():
    _, snapshot, _ = build_system()
    main(snapshot)


if __name__ == "__main__":
    run()