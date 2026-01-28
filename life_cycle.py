"""
A7DO Life Cycle Orchestrator
===========================

Single authoritative execution spine for A7DO.

Enforces:
- One clock (TickEngine)
- Phase separation (Womb → Birth → Living)
- Deterministic world evolution (Phase 0 compliant)
- No hidden side-effects

World remains pure physics + events.
Mind interprets; world does not think.
"""

from engine.tick_engine import TickEngine

# Genesis / Phases
from genesis.phase import Phase
from genesis.prebirth.phases import WOMB
from genesis.birth.criteria import birth_ready
from genesis.birth.transition import BirthTransition

# Core equilibrium
from square.state import SquareState

# World (Phase 0)
from world.world_state import make_default_world
from world.world_runner import WorldRunner

# Being / Embodiment
from embodiment.boundaries import Boundaries
from embodiment.ownership import Ownership

# Mind & memory
from mind.coherence import Coherence
from frames.store import FrameStore
from memory.structural_memory import StructuralMemory

# Accounting
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
    """

    def __init__(self):
        # ---------------- Core ----------------
        self.square = SquareState()
        self.engine = TickEngine(square=self.square)

        # ---------------- World ----------------
        self.world = make_default_world()
        self.world_runner = WorldRunner(self.world)

        # ---------------- Being ----------------
        self.boundaries = Boundaries()
        self.ownership = Ownership()

        # ---------------- Mind & Memory ----------------
        self.coherence = Coherence()
        self.frames = FrameStore()
        self.memory = StructuralMemory()

        # ---------------- Accounting ----------------
        self.accountant = Accountant()

        # ---------------- Genesis ----------------
        self.phase = Phase(WOMB)
        self.birth_transition = BirthTransition()
        self.born = False

        # Gates closed at start
        GateManager.close_all()

        # Engine phase binding
        self.engine.set_phase(WOMB)

    # ==================================================
    # One heartbeat of existence
    # ==================================================

    def tick(self):
        # Advance time (only clock)
        self.engine.tick()

        # Phase-0 world step (no action in womb)
        self.world_runner.step(action=None)

        if not self.born:
            self._womb_step()
        else:
            self._living_step()

    # ==================================================
    # WOMB (Pre-birth)
    # ==================================================

    def _womb_step(self):
        # Passive perception only
        perception_loop(
            world=self.world,
            embodiment=None,
            mind=self.coherence,
        )

        # Frames: fragments only
        self.frames.update(fragment_only=True)

        # Memory crystallization
        self.memory.update(self.frames)

        # Equilibrium evolution
        self.square.update()

        # Accounting without agency
        self.accountant.update(
            frames=self.frames,
            memory=self.memory,
            square=self.square,
        )

        # Birth condition
        if birth_ready(self):
            self._birth()

    # ==================================================
    # BIRTH (Irreversible)
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
    # POST-BIRTH (Living System)
    # ==================================================

    def _living_step(self):
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

        # Embodiment
        self.boundaries.update(self.world)
        self.ownership.update(self.boundaries)

        # Frame construction
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
    # Run loop
    # ==================================================

    def run(self, max_ticks: int | None = None):
        ticks = 0
        while True:
            self.tick()
            ticks += 1

            if max_ticks is not None and ticks >= max_ticks:
                break
