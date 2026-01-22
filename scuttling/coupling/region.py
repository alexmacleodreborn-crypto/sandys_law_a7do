from __future__ import annotations

from dataclasses import dataclass


# ============================================================
# Local State Doctrine
#
# LocalState represents the immediate embodied condition
# of a body region or local subsystem.
#
# It is:
# - non-symbolic
# - non-memory
# - non-gated
# - continuously updated
#
# LocalState does NOT:
# - reason
# - decide goals
# - store knowledge
#
# It only exposes physical readiness and constraint.
# ============================================================


@dataclass
class LocalState:
    """
    Local embodied state for a region or subsystem.
    """

    # ---------------------------------
    # Core structural signals
    # ---------------------------------

    load: float = 0.0          # [0..1] mechanical / effort load
    stability: float = 0.5     # [0..1] structural stability
    fatigue: float = 0.0       # [0..1] accumulated strain
    integrity: float = 1.0     # [0..1] tissue / system health

    # ---------------------------------
    # Safety clamps
    # ---------------------------------

    MAX_LOAD: float = 1.0
    MAX_FATIGUE: float = 1.0
    MIN_INTEGRITY: float = 0.0

    # ========================================================
    # Update methods (pure structural)
    # ========================================================

    def apply_load(self, delta: float) -> None:
        """
        Apply additional load to the local system.
        """
        self.load = min(self.MAX_LOAD, max(0.0, self.load + delta))

        # Load increases fatigue nonlinearly
        if delta > 0:
            self.fatigue = min(
                self.MAX_FATIGUE,
                self.fatigue + (delta * 0.5),
            )

        self._recompute_stability()

    def relieve_load(self, delta: float) -> None:
        """
        Reduce load (e.g. via reflex withdrawal or release).
        """
        self.load = max(0.0, self.load - abs(delta))
        self._recompute_stability()

    def apply_damage(self, severity: float) -> None:
        """
        Apply integrity damage (rare, conservative).
        """
        self.integrity = max(
            self.MIN_INTEGRITY,
            self.integrity - abs(severity),
        )
        self._recompute_stability()

    def recover(self, rate: float = 0.02) -> None:
        """
        Passive recovery when idle.
        """
        self.fatigue = max(0.0, self.fatigue - rate)
        self.load = max(0.0, self.load - rate)
        self._recompute_stability()

    # ========================================================
    # Internal logic
    # ========================================================

    def _recompute_stability(self) -> None:
        """
        Stability decreases with load and fatigue,
        increases with integrity.
        """
        self.stability = max(
            0.0,
            min(
                1.0,
                self.integrity
                * (1.0 - self.load)
                * (1.0 - self.fatigue),
            ),
        )

    # ========================================================
    # Read-only helpers
    # ========================================================

    def overloaded(self) -> bool:
        return self.load >= 0.85

    def unstable(self) -> bool:
        return self.stability <= 0.35

    def exhausted(self) -> bool:
        return self.fatigue >= 0.8