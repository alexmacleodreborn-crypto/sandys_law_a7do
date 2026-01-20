# sandys_law_a7do/sandy_law/collapse_conditions.py

from dataclasses import dataclass


@dataclass(frozen=True)
class CollapseReport:
    collapsed: bool
    reason: str
    severity: float


def collapse_triggered(
    *,
    coherence: float,
    fragmentation: float,
    pressure: float,
) -> CollapseReport:
    """
    Determines whether structural collapse occurs.

    Collapse is not failure — it is transition.
    """

    if coherence < 0.2 and fragmentation > 0.8:
        return CollapseReport(
            collapsed=True,
            reason="structure_lost",
            severity=1.0,
        )

    if pressure > 0.9 and coherence < 0.4:
        return CollapseReport(
            collapsed=True,
            reason="overpressure",
            severity=pressure,
        )

    return CollapseReport(
        collapsed=False,
        reason="stable",
        severity=0.0,
    )
