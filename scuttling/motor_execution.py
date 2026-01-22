# sandys_law_a7do/scuttling/motor_execution.py

from dataclasses import dataclass
from typing import Dict

from sandys_law_a7do.scuttling.motor_patterns import MotorPattern
from sandys_law_a7do.scuttling.body_map import BodyMap
from sandys_law_a7do.scuttling.coupling import CouplingGraph, propagate_once
from sandys_law_a7do.scuttling.load_reduction import decide_load_reduction


@dataclass
class MotorExecutionResult:
    """
    Structural outcome of executing a motor pattern.
    """
    resulting_load: float
    resulting_stability: float
    reduction_applied: bool
    reason: str


def execute_motor_pattern(
    *,
    pattern: MotorPattern,
    body_map: BodyMap,
    coupling: CouplingGraph,
    initial_load: float,
) -> MotorExecutionResult:
    """
    Execute a motor pattern as a physical process.

    This does NOT select the pattern.
    It only evaluates structural consequences.
    """

    # ---------------------------------
    # 1. Propagate load through body
    # ---------------------------------
    propagated = propagate_once(
        graph=coupling,
        source_regions=body_map.regions,
        load=initial_load + pattern.load_cost,
    )

    resulting_load = propagated.total_load

    # ---------------------------------
    # 2. Decide if complexity must reduce
    # ---------------------------------
    reduction = decide_load_reduction(
        load=resulting_load,
        stability=pattern.stability,
    )

    # ---------------------------------
    # 3. Update stability structurally
    # ---------------------------------
    stability = pattern.stability

    if reduction.reduction == "halt":
        stability *= 0.85
    elif reduction.reduction == "simplify":
        stability *= 0.95
    else:
        # Successful execution under load slightly reinforces
        stability = min(1.0, stability + 0.02)

    return MotorExecutionResult(
        resulting_load=resulting_load,
        resulting_stability=stability,
        reduction_applied=reduction.reduction != "none",
        reason=reduction.reason,
    )