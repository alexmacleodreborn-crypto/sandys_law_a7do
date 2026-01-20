# sandys_law_a7do/roles/sled_interface.py

from typing import Dict, Any
from .base_role import BaseRole


class SLEDInterface(BaseRole):
    """
    Adapter role between A7DO and SLED-like external systems.
    """

    def __init__(self):
        super().__init__(name="sled_interface")
        self.last_payload: Dict[str, Any] | None = None

    def receive(self, payload: Dict[str, Any]) -> None:
        """
        Receive structured input from SLED.
        """
        self.last_payload = payload

    def emit(self) -> Dict[str, Any] | None:
        """
        Emit structured output back to SLED.
        """
        return self.last_payload

    def tick(self) -> None:
        """
        No-op unless integrated by SystemManager.
        """
        pass
