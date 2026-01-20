# tools/reply.py

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class Reply:
    """
    Structured reply container.

    This is a transport / formatting utility only.
    """
    message: str
    level: str = "info"          # info | warning | error | debug
    payload: Optional[Dict[str, Any]] = None


def info(message: str, payload: Optional[Dict[str, Any]] = None) -> Reply:
    return Reply(message=message, level="info", payload=payload)


def warning(message: str, payload: Optional[Dict[str, Any]] = None) -> Reply:
    return Reply(message=message, level="warning", payload=payload)


def error(message: str, payload: Optional[Dict[str, Any]] = None) -> Reply:
    return Reply(message=message, level="error", payload=payload)


def debug(message: str, payload: Optional[Dict[str, Any]] = None) -> Reply:
    return Reply(message=message, level="debug", payload=payload)
