# interfaces/chat/chat_adapter.py

from typing import Any, Dict
from tools.reply import Reply, info, warning


class ChatAdapter:
    """
    Converts internal signals into chat-friendly replies.
    """

    def system_status(self, snapshot: Dict[str, Any]) -> Reply:
        if not snapshot:
            return warning("System snapshot empty")

        return info(
            message="System status available",
            payload=snapshot,
        )
