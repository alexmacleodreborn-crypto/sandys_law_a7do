from typing import Dict


# ============================================================
# DEFAULT ANATOMY
# ============================================================

def create_default_anatomy() -> Dict[str, Dict[str, float]]:
    """
    Biological anatomy scaffold.
    Growth and stability are in [0, 1].
    """
    parts = [
        # Core
        "head",
        "neck",
        "spine",
        "torso",
        "pelvis",

        # Sensory organs
        "eyes",
        "ears",
        "nose",
        "mouth",
        "tongue",

        # Upper limbs
        "left_arm",
        "right_arm",
        "left_hand",
        "right_hand",
        "left_fingers",
        "right_fingers",

        # Lower limbs
        "left_leg",
        "right_leg",
        "left_foot",
        "right_foot",
        "left_toes",
        "right_toes",

        # Other
        "skin",
        "genitalia",
        "umbilical",
    ]

    return {
        p: {"growth": 0.0, "stability": 0.0}
        for p in parts
    }


# ============================================================
# GROWTH SCHEDULE (BIOLOGICAL)
# ============================================================

# Relative growth priority (higher = earlier / faster)
GROWTH_PRIORITY = {
    "head": 1.4,
    "spine": 1.3,
    "torso": 1.2,
    "neck": 1.1,
    "pelvis": 1.0,

    "eyes": 0.9,
    "ears": 0.9,
    "nose": 0.8,
    "mouth": 0.8,
    "tongue": 0.7,

    "left_arm": 0.8,
    "right_arm": 0.8,
    "left_leg": 0.7,
    "right_leg": 0.7,

    "left_hand": 0.6,
    "right_hand": 0.6,
    "left_foot": 0.6,
    "right_foot": 0.6,

    "left_fingers": 0.4,
    "right_fingers": 0.4,
    "left_toes": 0.4,
    "right_toes": 0.4,

    "skin": 0.9,
    "genitalia": 0.3,
    "umbilical": 1.5,
}


# ============================================================
# ANATOMY GROWTH ENGINE
# ============================================================

def grow_anatomy(
    *,
    anatomy: Dict[str, Dict[str, float]],
    stability: float,
) -> None:
    """
    Apply one tick of biological growth.
    Called ONLY during gestation (pre-birth).
    """

    for part, data in anatomy.items():
        priority = GROWTH_PRIORITY.get(part, 0.5)

        # Slow, stability-gated growth
        delta = 0.002 * stability * priority

        # Growth
        new_growth = min(1.0, data["growth"] + delta)
        data["growth"] = new_growth

        # Stability lags growth slightly
        data["stability"] = min(
            1.0,
            data["stability"] + delta * 0.6,
        )


# ============================================================
# SNAPSHOT (READ-ONLY)
# ============================================================

def anatomy_snapshot(anatomy: Dict[str, Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """
    UI-safe snapshot.
    """
    return {
        part: {
            "growth": round(data["growth"], 3),
            "stability": round(data["stability"], 3),
        }
        for part, data in anatomy.items()
    }