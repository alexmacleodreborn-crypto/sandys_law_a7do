"""
Anatomy — Passive Biological Structure (LOCKED)

Doctrine:
- Defines WHAT body parts exist
- Defines HOW developed they are
- Does NOT learn
- Does NOT activate
- Does NOT couple
- Does NOT decay
- Grows deterministically during gestation
- Freezes structure at birth

This is NOT a body schema.
This is NOT proprioception.
This is NOT ownership.

It is anatomy.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict


# ============================================================
# BASIC REGION
# ============================================================

@dataclass
class AnatomyRegion:
    """
    Passive anatomical region.

    growth:   developmental completion [0.0 → 1.0]
    stability: structural integrity [0.0 → 1.0]
    present:  whether the region exists at all
    """
    present: bool = True
    growth: float = 0.0
    stability: float = 0.0

    def mature(self, amount: float) -> None:
        """
        Deterministic, monotonic growth.
        """
        if not self.present:
            return

        self.growth = min(1.0, self.growth + amount)
        self.stability = min(1.0, self.stability + amount * 0.8)


# ============================================================
# FULL ANATOMY
# ============================================================

@dataclass
class Anatomy:
    """
    Complete neonatal anatomical structure.

    Exists BEFORE movement.
    Exists BEFORE sensation.
    Exists BEFORE ownership.
    """

    # --------------------
    # Core body
    # --------------------
    head: AnatomyRegion
    neck: AnatomyRegion
    spine: AnatomyRegion
    torso: AnatomyRegion
    pelvis: AnatomyRegion

    # --------------------
    # Face & head organs
    # --------------------
    eyes: AnatomyRegion
    ears: AnatomyRegion
    nose: AnatomyRegion
    mouth: AnatomyRegion
    tongue: AnatomyRegion

    # --------------------
    # Upper limbs
    # --------------------
    left_arm: AnatomyRegion
    right_arm: AnatomyRegion
    left_hand: AnatomyRegion
    right_hand: AnatomyRegion
    fingers: AnatomyRegion

    # --------------------
    # Lower limbs
    # --------------------
    left_leg: AnatomyRegion
    right_leg: AnatomyRegion
    left_foot: AnatomyRegion
    right_foot: AnatomyRegion
    toes: AnatomyRegion

    # --------------------
    # Other biological
    # --------------------
    genitalia: AnatomyRegion
    umbilical: AnatomyRegion

    # ========================================================
    # GESTATIONAL GROWTH
    # ========================================================

    def grow(self, *, stability: float) -> None:
        """
        Apply one gestational growth step.

        stability is womb rhythmic stability [0.0 → 1.0]
        """

        base = 0.002 * stability

        # Core develops first
        self.head.mature(base * 1.5)
        self.spine.mature(base * 1.4)
        self.torso.mature(base * 1.4)
        self.pelvis.mature(base * 1.3)
        self.neck.mature(base * 1.2)

        # Face
        self.eyes.mature(base * 1.0)
        self.ears.mature(base * 1.0)
        self.nose.mature(base * 0.9)
        self.mouth.mature(base * 1.1)
        self.tongue.mature(base * 0.9)

        # Limbs
        self.left_arm.mature(base * 1.1)
        self.right_arm.mature(base * 1.1)
        self.left_hand.mature(base * 1.0)
        self.right_hand.mature(base * 1.0)
        self.fingers.mature(base * 0.9)

        self.left_leg.mature(base * 1.0)
        self.right_leg.mature(base * 1.0)
        self.left_foot.mature(base * 0.9)
        self.right_foot.mature(base * 0.9)
        self.toes.mature(base * 0.8)

        # Other
        self.genitalia.mature(base * 0.7)
        self.umbilical.mature(base * 1.6)


# ============================================================
# FACTORY
# ============================================================

def create_default_anatomy() -> Anatomy:
    """
    Create a baseline fetal anatomy.
    All regions exist but are immature.
    """
    def r() -> AnatomyRegion:
        return AnatomyRegion(present=True, growth=0.0, stability=0.0)

    return Anatomy(
        # Core
        head=r(),
        neck=r(),
        spine=r(),
        torso=r(),
        pelvis=r(),

        # Face
        eyes=r(),
        ears=r(),
        nose=r(),
        mouth=r(),
        tongue=r(),

        # Upper limbs
        left_arm=r(),
        right_arm=r(),
        left_hand=r(),
        right_hand=r(),
        fingers=r(),

        # Lower limbs
        left_leg=r(),
        right_leg=r(),
        left_foot=r(),
        right_foot=r(),
        toes=r(),

        # Other
        genitalia=r(),
        umbilical=r(),
    )


# ============================================================
# READ-ONLY SNAPSHOT (FOR UI)
# ============================================================

def anatomy_snapshot(anatomy: Anatomy) -> Dict[str, Dict[str, float]]:
    """
    Observer-safe snapshot for dashboards.
    """
    snap = {}
    for name, region in anatomy.__dict__.items():
        snap[name] = {
            "present": region.present,
            "growth": round(region.growth, 3),
            "stability": round(region.stability, 3),
        }
    return snap