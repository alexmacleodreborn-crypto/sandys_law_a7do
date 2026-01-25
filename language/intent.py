from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class LanguageIntent:
    """
    Structural intent extracted from language.

    This is NOT meaning.
    This is NOT belief.
    This is NOT truth.

    It is a routing hint only.
    """
    kind: str                 # "query", "request", "describe", "ack"
    target: Optional[str]     # "self", "system", "world", None
    confidence: float         # [0..1]