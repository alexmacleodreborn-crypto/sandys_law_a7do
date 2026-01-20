# sandys_law_a7do/gates/role_gate.py

from .base_gate import BaseGate, GateDecision


class RoleGate(BaseGate):
    """
    Determines whether a system role may execute.
    """

    def evaluate(
        self,
        *,
        role_name: str,
        allowed_roles: list[str],
    ) -> GateDecision:
        if role_name in allowed_roles:
            return GateDecision("allow", "role_authorized")

        return GateDecision("block", "role_not_authorized")
