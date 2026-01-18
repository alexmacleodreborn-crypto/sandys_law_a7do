from __future__ import annotations

from typing import Iterable

from frames.frame import Frame
from frames.fragment import Fragment

from embodiment.boundaries import BoundaryMap
from embodiment.ownership import OwnershipResolver
from embodiment.ledger import EmbodimentLedger
from embodiment.thermal_pain import ThermalPainProcessor


# ============================================================
# Embodiment Observer
#
# Passive observer of CLOSED frames only.
# Does NOT modify frames or world.
# ============================================================

class EmbodimentObserver:
    def __init__(
        self,
        *,
        boundaries: BoundaryMap,
        ownership: OwnershipResolver,
        ledger: EmbodimentLedger,
        thermal: ThermalPainProcessor,
    ) -> None:
        self.boundaries = boundaries
        self.ownership = ownership
        self.ledger = ledger
        self.thermal = thermal

    # --------------------------------------------------------
    # Observe a closed frame
    # --------------------------------------------------------

    def observe_frame(self, frame: Frame) -> None:
        if not frame.closed:
            return  # embodiment only sees settled information

        for fragment in frame.fragments:
            self._observe_fragment(fragment)

    # --------------------------------------------------------
    # Fragment handling
    # --------------------------------------------------------

    def _observe_fragment(self, fragment: Fragment) -> None:
        if fragment.kind == "contact":
            self._handle_contact(fragment)

        elif fragment.kind == "thermal":
            self._handle_thermal(fragment)

        elif fragment.kind == "force":
            self._handle_force(fragment)

    # --------------------------------------------------------
    # Handlers
    # --------------------------------------------------------

    def _handle_contact(self, fragment: Fragment) -> None:
        x = fragment.payload.get("x")
        y = fragment.payload.get("y")

        if x is None or y is None:
            return

        regions = self.boundaries.detect_contact(x, y)
        for region in regions:
            ownership = self.ownership.resolve(region)
            if ownership.owned:
                self.ledger.record_contact(region)

    def _handle_thermal(self, fragment: Fragment) -> None:
        region = fragment.payload.get("region")
        delta = fragment.payload.get("delta")

        if region is None or delta is None:
            return

        ownership = self.ownership.resolve(region)
        if ownership.owned:
            signal = self.thermal.thermal_to_signal(region, delta)
            self.ledger.record_thermal(signal.region, signal.temperature_delta)

    def _handle_force(self, fragment: Fragment) -> None:
        region = fragment.payload.get("region")
        force = fragment.payload.get("force")

        if region is None or force is None:
            return

        ownership = self.ownership.resolve(region)
        if ownership.owned:
            pain = self.thermal.pain_from_contact(region, force)
            self.ledger.record_pain(pain.region)
