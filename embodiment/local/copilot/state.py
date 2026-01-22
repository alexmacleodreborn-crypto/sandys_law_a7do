# sandys_law_a7do/embodiment/local/copilot/state.py
"""
Local Copilot State — Phase A4.1 (LOCKED)

Defines:
- Local autonomy state per body region
- Whether region is acting reflexively
- Whether escalation is required

No decisions.
No learning.
No memory writes.
"""

from dataclasses import dataclass


@dataclass
class CopilotState:
    """
    Represents the control state of a local region.
    """
    active: bool = False
    overloaded: bool = False
    confidence: float = 0.0   # [0..1], procedural confidence only
    last_reason: str | None = None