from dataclasses import dataclass


@dataclass(frozen=True)
class Utterance:
    """
    A surface-language response.

    This carries NO authority.
    It is a rendering of structure.
    """
    text: str
    certainty: float          # [0..1]