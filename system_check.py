"""
A7DO System Coherence Check
==========================

Structural + wiring pre-flight check.

- Verifies file presence
- Verifies imports
- Verifies LifeCycle instantiation
- Verifies Phase-0 world stepping

Does NOT advance time.
Does NOT mutate long-term state.
"""

import importlib
from pathlib import Path


# --------------------------------------------------
# Required files
# --------------------------------------------------

REQUIRED_PATHS = [
    "life_cycle.py",
    "engine/tick_engine.py",
    "genesis/prebirth/phases.py",
    "genesis/birth/criteria.py",
    "genesis/birth/transition.py",
    "square/state.py",
    "world/world_state.py",
    "world/world_runner.py",
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
    "world.world_runner",
    "frames.store",
    "memory.structural_memory",
    "accounting.accountant",
    "gates.gate_manager",
]


# --------------------------------------------------
# Checks
# --------------------------------------------------

def check_paths() -> bool:
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


def check_imports() -> bool:
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


def check_lifecycle_instantiation() -> bool:
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


def check_world_step() -> bool:
    print("🔍 Checking Phase-0 WorldRunner step...")
    try:
        from world.world_state import make_default_world
        from world.world_runner import WorldRunner

        world = make_default_world()
        runner = WorldRunner(world)
        events = runner.step(action=(1, 0))

        assert isinstance(events, list)
    except Exception as e:
        print("❌ WorldRunner step failed:")
        print(f"   {e}")
        return False

    print("✅ WorldRunner step OK")
    return True


# --------------------------------------------------
# Run all checks
# --------------------------------------------------

def run_check() -> bool:
    print("\n🧠 A7DO SYSTEM CHECK")
    print("=" * 32)

    ok = True
    ok &= check_paths()
    ok &= check_imports()
    ok &= check_lifecycle_instantiation()
    ok &= check_world_step()

    if ok:
        print("\n🎉 SYSTEM CHECK PASSED")
        print("A7DO is structurally coherent and Phase-0 compliant.")
    else:
        print("\n⚠️ SYSTEM CHECK FAILED")
        print("Fix issues above before running LifeCycle.")

    return ok


if __name__ == "__main__":
    run_check()
