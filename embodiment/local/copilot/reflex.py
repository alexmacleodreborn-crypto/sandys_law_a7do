# sandys_law_a7do/embodiment/local/copilot/reflex.py
"""
Local Reflex Resolver — Phase A4.1 (LOCKED)

Purpose:
- Decide whether a local region can resolve an event
- Or must escalate to regional / global processing

No gates.
No learning.
Pure structural logic.
"""

from sandys_law_a7do.embodiment.local.copilot.state import CopilotState


def resolve_reflex(
    *,
    load: float,
    stability: float,
    confidence: float,
) -> CopilotState:
    """
    Determines whether reflex control is allowed.

    Rules:
    - High confidence + low load → local autonomy
    - High load or low stability → escalate
    """

    if load > 0.85:
        return CopilotState(
            active=False,
            overloaded=True,
            confidence=confidence,
            last_reason="overload",
        )

    if confidence > 0.6 and stability > 0.5:
        return CopilotState(
            active=True,
            overloaded=False,
            confidence=confidence,
            last_reason="stable_reflex",
        )

    return CopilotState(
        active=False,
        overloaded=False,
        confidence=confidence,
        last_reason="insufficient_confidence",
    )