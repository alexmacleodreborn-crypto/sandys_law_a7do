# sandys_law_a7do/bootstrap.py
"""
Bootstrap — v1.6 (LOCKED)

Implements:
- Frame lifecycle
- System snapshot
- Tick counter
- OPTION A: Episode commit on frame close
- Controlled perceptual diversity (Phase 4.1)
- Coherence ⇄ Perception coupling (Phase 4.2)
- Structural load & stability divergence (Phase 5)
- Preference drift update on episode close (Phase 6) — READ-ONLY BIAS

Plus wiring:
- PerceptionGate controls fragment intake
- ConsolidationGate tags consolidation readiness

MemoryTrace signature (AUTHORITATIVE):
MemoryTrace(
    tick,
    Z,
    coherence,
    stability,
    frame_signature,
    weight=1.0,
    tags=[...]
)
"""

from __future__ import annotations

from sandys_law_a7do.frames.store import FrameStore
from sandys_law_a7do.frames.frame import Frame

from sandys_law_a7do.mind.coherence import compute_coherence
from sandys_law_a7do.mind.regulation import regulate
from sandys_law_a7do.mind.perception import summarize_perception

from sandys_law_a7do.mind.preference import (
    PreferenceEngine,
    PreferenceStore,
    PreferenceConfig,
)

from sandys_law_a7do.memory.trace import MemoryTrace
from sandys_law_a7do.memory.structural_memory import StructuralMemory

from sandys_law_a7do.integration.perception_loop import perceive_and_act

# Gates (already exist in your repo)
from sandys_law_a7do.gates.perception_gate import PerceptionGate
from sandys_law_a7do.gates.consolidation_gate import ConsolidationGate


def build_system():
    frames = FrameStore()
    memory = StructuralMemory()

    # Phase 6 — preference (in-memory)
    pref_store = PreferenceStore()
    pref_engine = PreferenceEngine(store=pref_store, cfg=PreferenceConfig())

    state = {
        "frames": frames,
        "memory": memory,
        "ticks": 0,

        # Phase 5 — temporal structural pressure
        "structural_load": 0.0,

        # Phase 6 — read-only bias system
        "preference_engine": pref_engine,
        "preference_store": pref_store,
        "last_preference_update": None,

        # surfaced channels
        "last_attention": 1.0,
    }

    def snapshot():
        return system_snapshot(state)

    return snapshot, state


def _extract_attention_stats(active_frame) -> tuple[float, float]:
    """
    Read-only extraction: attention is carried in fragment.payload['attention'].
    Returns (last_attention, avg_attention).
    """
    if not active_frame or not getattr(active_frame, "fragments", None):
        return 1.0, 1.0

    vals = []
    for f in active_frame.fragments:
        try:
            vals.append(float(getattr(f, "payload", {}).get("attention", 1.0)))
        except Exception:
            vals.append(1.0)

    if not vals:
        return 1.0, 1.0

    return float(vals[-1]), float(sum(vals) / len(vals))


def system_snapshot(state: dict) -> dict:
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    active = frames.active

    if active:
        fragments = [{"action": f.kind} for f in active.fragments]
        percept = summarize_perception(fragments)
    else:
        percept = summarize_perception([])

    report = compute_coherence(
        fragment_count=percept.fragment_count,
        unique_actions=percept.unique_actions,
        blocked_events=0,
        percept_notes=percept.notes,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    regulation = regulate(
        coherence=coherence,
        fragmentation=Z,
        block_rate=report.block_rate,
    )

    # Phase 6 — expose top preferences (read-only)
    pref_store: PreferenceStore = state["preference_store"]
    top_contexts = pref_store.top(10)

    # Attention surfaced (read-only)
    att_last, att_avg = _extract_attention_stats(active)
    state["last_attention"] = float(att_last)

    return {
        "ticks": state["ticks"],
        "metrics": {
            "Z": Z,
            "Coherence": coherence,
            "Stability": stability,
            "Load": load,
            "AttentionLast": float(att_last),
            "AttentionAvg": float(att_avg),
            "PredErr": float(state.get("prediction_error", 0.0)),
        },
        "regulation": regulation,
        "active_frame": active,
        "memory_count": memory.count(),
        "preference_top": [{"context": k, "score": v} for (k, v) in top_contexts],
        "last_preference_update": state.get("last_preference_update"),
    }


def open_frame(state: dict):
    if state["frames"].active:
        return

    frame = Frame(domain="demo", label="ui")
    state["frames"].open(frame)


def add_fragment(state: dict):
    """
    Phase 4.1 — Controlled Perceptual Diversity
    Now gate-controlled by PerceptionGate.
    """
    frame = state["frames"].active
    if not frame:
        return

    # Gate based on latest known channels (fallback safe)
    coherence = float(state.get("last_coherence", 0.0))
    fragmentation = float(state.get("last_fragmentation", 0.0))
    block_rate = float(state.get("last_block_rate", 0.0))

    gate = PerceptionGate()
    decision = gate.evaluate(block_rate=block_rate, fragmentation=fragmentation)

    if getattr(decision, "state", "allow") != "allow":
        # Do not add fragments if perception is gated.
        return

    fragments = perceive_and_act(state)
    for frag in fragments:
        state["frames"].add_fragment(frag)


def close_frame(state: dict):
    """
    OPTION A — EPISODE COMMIT ON FRAME CLOSE

    Phase 6 addition:
    - Update PreferenceEngine with structural context derived from percept + metrics
    - Store only a bias score for context keys (no actions, no reward)

    Gate wiring:
    - ConsolidationGate tags whether consolidation conditions were met
    """
    frames: FrameStore = state["frames"]
    memory: StructuralMemory = state["memory"]

    frame = frames.active
    if not frame:
        return

    fragments = [{"action": f.kind} for f in frame.fragments]
    percept = summarize_perception(fragments)

    report = compute_coherence(
        fragment_count=percept.fragment_count,
        unique_actions=percept.unique_actions,
        blocked_events=0,
        percept_notes=percept.notes,
    )

    Z = float(report.fragmentation)
    coherence = float(report.coherence)

    load = float(state.get("structural_load", 0.0))
    stability = coherence * (1.0 - load)

    # Gate: consolidation readiness (tag only)
    c_gate = ConsolidationGate()
    c_decision = c_gate.evaluate(coherence=coherence, fragmentation=Z)
    c_state = getattr(c_decision, "state", "defer")
    c_reason = getattr(c_decision, "reason", "unknown")

    tags = ["episode", "stable" if stability >= 0.7 else "unstable"]
    tags.append(f"consolidation:{c_state}")

    trace = MemoryTrace(
        state["ticks"],
        Z,
        coherence,
        stability,
        f"{frame.domain}:{frame.label}",
        1.0,
        tags,
    )
    memory.add_trace(trace)

    # ---- Phase 6: Preference update (READ-ONLY BIAS) ----
    pref_engine: PreferenceEngine = state["preference_engine"]

    context_key = pref_engine.context_key_from_accounting(
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        notes=percept.notes,
    )

    update = pref_engine.update(
        context_key=context_key,
        coherence=coherence,
        fragmentation=Z,
        block_rate=float(report.block_rate),
        prediction_error_l1=state.get("prediction_error", None),
    )

    state["last_preference_update"] = {
        "tick": state["ticks"],
        "context": update.context_key,
        "previous": update.previous,
        "updated": update.updated,
        "delta": update.delta,
        "reason": update.reason,
        "consolidation_gate": {"state": c_state, "reason": c_reason},
    }

    # ---- Resolution releases pressure ----
    state["structural_load"] *= 0.6
    frames.close()


def tick_system(state: dict):
    """
    Phase 5 — Temporal structural pressure

    - Load increases when a frame remains open
    - Load decays when no frame is active
    """
    state["ticks"] += 1

    frames = state["frames"]
    load = float(state.get("structural_load", 0.0))

    if frames.active:
        load += 0.05
    else:
        load *= 0.6

    state["structural_load"] = max(0.0, min(1.0, load))