# sandys_law_a7do/genesis/phase.py

from __future__ import annotations
from enum import Enum, auto
from typing import Dict

from sandys_law_a7do.genesis.birth import BirthEvaluator, BirthState


class GenesisPhase(Enum):
    PREBIRTH = auto()
    POSTBIRTH = auto()


class GenesisController:
    """
    Sole authority for genesis phase.
    """

    def __init__(self) -> None:
        self._phase = GenesisPhase.PREBIRTH
        self._birth_evaluator = BirthEvaluator()
        self._birth_state: BirthState | None = None

    def update(
        self,
        *,
        tick: int,
        metrics: Dict[str, float],
    ) -> GenesisPhase:
        if self._phase is GenesisPhase.POSTBIRTH:
            return self._phase

        birth_state = self._birth_evaluator.evaluate(
            tick=tick,
            metrics=metrics,
        )

        self._birth_state = birth_state

        if birth_state.born:
            self._phase = GenesisPhase.POSTBIRTH

        return self._phase

    @property
    def phase(self) -> GenesisPhase:
        return self._phase

    @property
    def birth_state(self) -> BirthState | None:
        return self._birth_state