"""
A7DO Life Cycle Orchestrator
===========================

This file is the single authoritative execution spine for A7DO.

It enforces:
- One clock (TickEngine)
- One phase at a time (Genesis)
- Ordered subsystem updates
- Womb → Birth → World life coherence

Nothing acts outside this loop.
"""

from engine.tick_engine import TickEngine

# Genesis / Phases
from genesis.phase import Phase
from genesis.prebirth.phases import WOMB
from genesis.birth.transition import BirthTransition
from genesis.birth.criteria import birth_ready

# Core state
from square.state import SquareState

# Subsystems
from world.world_state import WorldState
from embodiment.boundaries import Boundaries
from embodiment.ownership import Ownership
from mind.coherence import Coherence
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory
from accounting.accountant import Accountant

# Integration loops
from integration.perception_loop import perception_loop
from integration.phase1_loop import phase1_loop
from integration.phase2_loop import phase2_loop

# Gates
from gates.gate_manager import GateManager


class LifeCycle:
    """
    The only place where time advances.

    Order is intentional and MUST NOT be changed casually.
    """

    def __init__(self):
        # --- Core ---
        self.square = SquareState()
        self.engine = TickEngine(square=self.square)

        # --- World ---
        self.world = WorldState()

        # --- Being ---
        self.boundaries = Boundaries()
        self.ownership = Ownership()

        # --- Mind & Memory ---
        self.coherence = Coherence()
        self.frames = FrameStore()
        self.memory = StructuralMemory()

        # --- Accounting ---
        self.accountant = Accountant()

        # --- Genesis ---
        self.phase = Phase(WOMB)
        self.birth_transition = BirthTransition()

        # --- State flags ---
        self.born = False

        # Initialize gates closed
        GateManager.close_all()

        # Bind engine phase
        self.engine.set_phase(WOMB)

    # --------------------------------------------------
    # One tick of existence
    # --------------------------------------------------

    def tick(self):
        """
        A single heartbeat of A7DO.
        """

        # 1. Advance time
        self.engine.tick()

        # 2. Update world (always exists)
        self.world.update()

        # 3. Pre-birth (WOMB)
        if not self.born:
            self._womb_step()
        else:
            self._living_step()

    # --------------------------------------------------
    # WOMB LOGIC
    # --------------------------------------------------

    def _womb_step(self):
        """
        Pre-birth: structure forms, no agency.
        """

        # Passive perception only
        perception_loop(
            world=self.world,
            embodiment=None,
            mind=self.coherence,
        )

        # Frames are fragments only
        self.frames.update(fragment_only=True)

        # Memory crystallizes slowly
        self.memory.update(self.frames)

        # Square stability evolves
        self.square.update()

        # Accounting still runs (self-measurement without action)
        self.accountant.update(
            frames=self.frames,
            memory=self.memory,
            square=self.square,
        )

        # Check birth condition
        if birth_ready(self):
            self._birth()

    # --------------------------------------------------
    # BIRTH EVENT
    # --------------------------------------------------

    def _birth(self):
        """
        One-way irreversible transition.
        """

        self.birth_transition.execute()

        # Open required gates
        GateManager.open("perception")
        GateManager.open("motor")
        GateManager.open("identity")

        self.born = True

        # Advance phase
        self.phase.advance()
        self.engine.set_phase(self.phase.current)

    # --------------------------------------------------
    # POST-BIRTH (LIVING SYSTEM)
    # --------------------------------------------------

    def _living_step(self):
        """
        Infant → child → agent lifecycle.
        """

        # Phase-specific integration
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

        # Ownership & embodiment update
        self.boundaries.update(self.world)
        self.ownership.update(self.boundaries)

        # Frame construction
        self.frames.update(
            embodiment=self.boundaries,
            mind=self.coherence,
            world=self.world,
        )

        # Memory update
        self.memory.update(self.frames)

        # Accounting & self-evaluation
        self.accountant.update(
            frames=self.frames,
            memory=self.memory,
            square=self.square,
        )

        # Square equilibrium
        self.square.update()

    # --------------------------------------------------
    # Run loop
    # --------------------------------------------------

    def run(self, max_ticks=None):
        """
        Run the life cycle.

        If max_ticks is None → run forever.
        """
        ticks = 0
        while True:
            self.tick()
            ticks += 1

            if max_ticks is not None and ticks >= max_ticks:
                break