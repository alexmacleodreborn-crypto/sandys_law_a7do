"""
A7DO System Coherence Check
==========================

Verifies:
- File structure
- Import wiring
- Lifecycle readiness

This does NOT run the system.
"""

import importlib
import sys
from pathlib import Path


REQUIRED_PATHS = [
    "engine/tick_engine.py",
    "genesis/prebirth/phases.py",
    "genesis/birth/criteria.py",
    "genesis/birth/transition.py",
    "square/state.py",
    "world/world_state.py",
    "frames/store.py",
    "memory/structural_memory.py",
    "accounting/accountant.py",
    "gates/gate_manager.py",
    "integration/perception_loop.py",
]


REQUIRED_IMPORTS = [
    "engine.tick_engine",
    "genesis.prebirth.phases",
    "genesis.birth.criteria",
    "genesis.birth.transition",
    "square.state",
    "world.world_state",
    "frames.store",
    "memory.structural_memory",
    "accounting.accountant",
    "gates.gate_manager",
]


def check_paths():
    print("🔍 Checking file structure...")
    root = Path(__file__).parent

    missing = []
    for rel in REQUIRED_PATHS:
        if not (root / rel).exists():
            missing.append(rel)

    if missing:
        print("❌ Missing required files:")
        for m in missing:
            print(f"   - {m}")
        return False

    print("✅ File structure OK")
    return True


def check_imports():
    print("🔍 Checking imports...")
    failed = []

    for module in REQUIRED_IMPORTS:
        try:
            importlib.import_module(module)
        except Exception as e:
            failed.append((module, str(e)))

    if failed:
        print("❌ Import failures:")
        for mod, err in failed:
            print(f"   - {mod}: {err}")
        return False

    print("✅ Imports OK")
    return True


def check_lifecycle_instantiation():
    print("🔍 Checking LifeCycle instantiation...")

    try:
        from life_cycle import LifeCycle
        lc = LifeCycle()
    except Exception as e:
        print("❌ LifeCycle failed to initialize:")
        print(f"   {e}")
        return False

    print("✅ LifeCycle initializes cleanly")
    return True


def run_check():
    print("\n🧠 A7DO SYSTEM CHECK\n" + "=" * 30)

    ok = True
    ok &= check_paths()
    ok &= check_imports()
    ok &= check_lifecycle_instantiation()

    if ok:
        print("\n🎉 SYSTEM CHECK PASSED")
        print("A7DO is structurally coherent and ready to live.")
    else:
        print("\n⚠️ SYSTEM CHECK FAILED")
        print("Fix the issues above before running the life cycle.")

    return ok


if __name__ == "__main__":
    run_check()