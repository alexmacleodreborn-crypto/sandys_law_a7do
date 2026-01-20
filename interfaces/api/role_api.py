# interfaces/api/role_api.py

from typing import Dict, Any
from roles.system_manager import SystemManager


class RoleAPI:
    """
    External-facing API bound to system roles.
    """

    def __init__(self, system: SystemManager):
        self.system = system

    def list_roles(self) -> list[str]:
        return list(self.system.roles.keys())

    def role_snapshot(self, role_name: str) -> Dict[str, Any]:
        role = self.system.get(role_name)
        if role is None:
            return {"error": "role_not_found"}

        return {
            "name": role.name,
            "type": role.__class__.__name__,
        }
