# sandys_law_a7do/genesis/prebirth.py

"""
PREBIRTH PHASE — A7DO

Doctrine:
- No choice
- No agency
- No ownership
- No speech
- No consolidation
- No gate opening

Purpose:
- Allow structural shaping
- Allow reflex entrainment
- Allow sensory statistics
- Allow embodiment CANDIDATES ONLY

Prebirth is NOT learning.
Prebirth is NOT acting.
Prebirth is being constrained into form.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class PrebirthConstraints:
    # --------------------------------------------------
    # Agency
    # --------------------------------------------------
    allow_choice: bool = False
    allow_action_selection: bool = False
    allow_chat: bool = False

    # --------------------------------------------------
    # Embodiment
    # --------------------------------------------------
    allow_candidates: bool = True
    allow_consolidation: bool = False
    allow_ownership: bool = False

    # --------------------------------------------------
    # Scuttling
    # --------------------------------------------------
    allow_reflexes: bool = True
    allow_motor_patterns: bool = True
    allow_skills: bool = False

    # --------------------------------------------------
    # Accounting
    # --------------------------------------------------
    accountant_visible: bool = False
    accountant_internal_only: bool = True

    # --------------------------------------------------
    # Gates
    # --------------------------------------------------
    allow_gate_evaluation: bool = False