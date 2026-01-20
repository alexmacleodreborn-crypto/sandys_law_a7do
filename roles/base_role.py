# sandys_law_a7do/roles/base_role.py

from abc import ABC, abstractmethod


class BaseRole(ABC):
    """
    Abstract base for system roles.
    Roles coordinate actions but do not perform cognition.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def tick(self) -> None:
        """
        Periodic coordination hook.
        No timing assumptions.
        """
        raise NotImplementedError
