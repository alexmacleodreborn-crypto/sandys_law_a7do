# sandys_law_a7do/roles/system_manager.py

from typing import Dict
from .base_role import BaseRole


class SystemManager(BaseRole):
    """
    Top-level coordinator.
    Owns role registry and high-level orchestration.
    """

    def __init__(self):
        super().__init__(name="system_manager")
        self.roles: Dict[str, BaseRole] = {}

    def register(self, role: BaseRole) -> None:
        self.roles[role.name] = role

    def get(self, name: str) -> BaseRole | None:
        return self.roles.get(name)

    def tick(self) -> None:
        """
        Coordinate all registered roles.
        Order is explicit and deterministic.
        """
        for role in self.roles.values():
            role.tick()
