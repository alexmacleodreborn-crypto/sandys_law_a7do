from dataclasses import dataclass

@dataclass(frozen=True)
class BirthState:
    """
    Structural lifecycle state of A7DO.

    This is NOT memory.
    This is NOT embodiment.
    This is NOT belief.
    """
    prebirth: bool
    born: bool
    tick_of_birth: int | None
    reason: str