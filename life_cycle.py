"""
A7DO Full Life Cycle
===================

This is the single authoritative execution spine.

Properties:
- One clock
- Deterministic world
- Phase separation
- Irreversible birth
- First embodied movement post-birth

World = physics only
Mind = interpretation only
Agency = gated
"""

from typing import Optional, Tuple
import random

# --------------------------------------------------
# Core clock
# --------------------------------------------------

from engine.tick_engine import TickEngine

# --------------------------------------------------
# Genesis / Phases
# --------------------------------------------------

from genesis.phase import Phase
from genesis.prebirth.phases import WOMB
from genesis.birth.criteria import birth_ready
from genesis.birth.transition import BirthTransition

# --------------------------------------------------
# Equilibrium core
# --------------------------------------------------

from square.state import SquareState

# --------------------------------------------------
# World (Phase 0)
# --------------------------------------------------

from world.world_state import make_default_world
from world.world_runner import WorldRunner

# --------------------------------------------------
# Embodiment
# --------------------------------------------------

from embodiment.boundaries import Boundaries
from embodiment.ownership import Ownership

# --------------------------------------------------
# Mind & Memory
# --------------------------------------------------

from mind.coherence import Coherence
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory

# --------------------------------------------------
# Accounting
# --------------------------------------------------

from accounting.accountant import Accountant

# --------------------------------------------------
# Integration
# --------------------------------------------------

from integration.perception_loop import perception_loop
from integration.phase1_loop import phase1_loop
from integration.phase2_loop import phase2_loop

# --------------------------------------------------
# Gates
# --------------------------------------------------

from gates.gate_manager import GateManager


# ==================================================
# LIFE CYCLE
# ==================================================

class LifeCycle:
    """
    The only place where time advances.
    """

    def __init__(self):
        # ---------------- Clock ----------------
        self.square = SquareState()
        self.engine = TickEngine(square=self.square)

        # ---------------- World ----------------
        self.world = make_default_world()
        self.world_runner = WorldRunner(self.world)

        # ---------------- Being ----------------
        self.boundaries = Boundaries()
        self.ownership = Ownership()

        # ---------------- Mind ----------------
        self.coherence = Coherence()
        self.frames = FrameStore()
        self.memory = StructuralMemory()

        # ---------------- Accounting ----------------
        self.accountant = Accountant()

        # ---------------- Genesis ----------------
        self.phase = Phase(WOMB)
        self.birth_transition = BirthTransition()
        self.born = False

        # ---------------- Agency ----------------
        self.last_action: Optional[Tuple[int, int]] = None

        # Gates closed at start
        GateManager.close_all()

        # Bind phase to clock
        self.engine.set_phase(WOMB)

    # ==================================================
    # ONE HEARTBEAT
    # ==================================================

    def tick(self):
        # Advance time (only clock)
        self.engine.tick()

        # Decide action (only post-birth)
        action = self._decide_action() if self.born else None

        # Advance world physics (Phase 0 compliant)
        self.world_runner.step(action=action)

        # Phase-specific processing
        if not self.born:
            self._womb_step()
        else:
            self._living_step()

    # ==================================================
    # WOMB PHASE
    # ==================================================

    def _womb_step(self):
        # Passive perception only
        perception_loop(
            world=self.world,
            embodiment=None,
            mind=self.coherence,
        )

        # Fragment frames only
        self.frames.update(fragment_only=True)

        # Memory crystallization
        self.memory.update(self.frames)

        # Equilibrium evolution
        self.square.update()

        # Self-measurement without agency
        self.accountant.update(
            frames=self.frames,
            memory=self.memory,
            square=self.square,
        )

        # Birth condition
        if birth_ready(self):
            self._birth()

    # ==================================================
    # BIRTH EVENT (IRREVERSIBLE)
    # ==================================================

    def _birth(self):
        self.birth_transition.execute()

        GateManager.open("perception")
        GateManager.open("motor")
        GateManager.open("identity")

        self.born = True
        self.phase.advance()
        self.engine.set_phase(self.phase.current)

    # ==================================================
    # POST-BIRTH LIFE
    # ==================================================

    def _living_step(self):
        # Phase integration
        if self.phase.is_phase1():
            phase1_loop(
                world=self.world,
                embodiment=self.boundaries,
                mind=self.coherence,
            )
        else:
            phase2_loop(
                world=self.world,
                embodiment=self.boundaries,
                mind=self.coherence,
            )

        # Embodiment update
        self.boundaries.update(self.world)
        self.ownership.update(self.boundaries)

        # Full frame construction
        self.frames.update(
            embodiment=self.boundaries,
            mind=self.coherence,
            world=self.world,
        )

        # Memory
        self.memory.update(self.frames)

        # Accounting
        self.accountant.update(
            frames=self.frames,
            memory=self.memory,
            square=self.square,
        )

        # Equilibrium
        self.square.update()

    # ==================================================
    # ACTION SELECTION (INFANT REFLEX)
    # ==================================================

    def _decide_action(self) -> Optional[Tuple[int, int]]:
        """
        Phase-1 infant reflex:
        - Random local movement
        - No planning
        - No memory lookup
        """

        # Only move if motor gate is open
        if not GateManager.is_open("motor"):
            return None

        # Simple reflex directions
        directions = [
            (1, 0),
            (-1, 0),
            (0, 1),
            (0, -1),
        ]

        action = random.choice(directions)
        self.last_action = action
        return action

    # ==================================================
    # RUN LOOP
    # ==================================================

    def run(self, max_ticks: int | None = None):
        ticks = 0
        while True:
            self.tick()
            ticks += 1

            if max_ticks is not None and ticks >= max_ticks:
                break
