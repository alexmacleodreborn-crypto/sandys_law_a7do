# sandys_law_a7do/integration/perception_loop.py
"""
Perception Loop — Phase 6.1

Responsibilities:
- Generate perceptual fragments
- Annotate fragments with READ-ONLY attention bias
- NO action selection
- NO filtering
- NO memory writes
- NO learning

Attention is a soft scalar only.
"""

from typing import List

from sandys_law_a7do.frames.fragment import Fragment
from sandys_law_a7do.accounting.attention import compute_attention_gain


# --------------------------------------------------
# MAIN PERCEPTION LOOP
# --------------------------------------------------

def perceive_and_act(state: dict) -> List[Fragment]:
    """
    Phase 4–6 perception loop.

    Generates fragments and annotates them with
    preference-weighted attention (Phase 6.1).

    This function MUST remain:
    - deterministic
    - side-effect free (except fragment creation)
    """

    fragments: List[Fragment] = []

    # --------------------------------------------------
    # BASIC PERCEPTION (EXAMPLE / DEMO)
    # --------------------------------------------------
    # NOTE: This is intentionally simple.
    # Replace / expand later with sensors, walkers, etc.

    frag = Fragment(
        kind="contact",
        payload={"source": "demo"},
    )
    fragments.append(frag)

    # --------------------------------------------------
    # PHASE 6.1 — READ-ONLY ATTENTION
    # --------------------------------------------------

    attention_gain = 1.0  # default neutral

    pref_store = state.get("preference_store")
    pref_engine = state.get("preference_engine")

    if pref_store and pref_engine:
        try:
            # Use LAST KNOWN structural metrics if available
            coherence = float(state.get("last_coherence", 0.0))
            fragmentation = float(state.get("last_fragmentation", 0.0))
            block_rate = float(state.get("last_block_rate", 0.0))
            notes = state.get("last_percept_notes", [])

            context_key = pref_engine.context_key_from_accounting(
                coherence=coherence,
                fragmentation=fragmentation,
                block_rate=block_rate,
                notes=notes,
            )

            pref_score = pref_store.get(context_key)

            attention_gain = compute_attention_gain(
                preference_score=pref_score
            )

        except Exception:
            # HARD FAIL SAFE — perception must never break
            attention_gain = 1.0

    # --------------------------------------------------
    # ANNOTATE FRAGMENTS (NO FILTERING)
    # --------------------------------------------------

    for f in fragments:
        # Dynamic attribute is intentional (Phase 6.1)
        f.attention = attention_gain

    return fragments