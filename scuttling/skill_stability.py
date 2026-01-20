# sandys_law_a7do/scuttling/skill_stability.py

from dataclasses import dataclass


@dataclass(frozen=True)
class SkillStabilityReport:
    """
    Stability of a motor skill.
    """
    stability: float     # [0..1]
    degraded: bool
    reason: str


def assess_skill_stability(
    *,
    repetitions: int,
    failures: int,
) -> SkillStabilityReport:
    """
    Computes skill stability from repetition vs failure.
    """
    if repetitions <= 0:
        return SkillStabilityReport(0.0, True, "no_practice")

    fail_rate = failures / max(1, repetitions)
    stability = max(0.0, 1.0 - fail_rate)

    return SkillStabilityReport(
        stability=stability,
        degraded=stability < 0.4,
        reason="degraded" if stability < 0.4 else "stable",
    )
