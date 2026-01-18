Gates
Information Flow as Structure (Not Rules)
1. Definition

A Gate is the only mechanism by which information may move between subsystems in A7DO.

A gate is:

a structural coupling

deterministic

directional

conditional

A gate is not:

a rule

a permission

a policy

a reward mechanism

a moral constraint

If a gate is closed, information cannot propagate.
Nothing is “forbidden” — the connection simply does not exist.

2. Why Gates Replace Rules

Rules can be bypassed.
Permissions can be escalated.
Policies can be optimized against.

Physical systems do not use rules.
They use available couplings.

A7DO therefore enforces safety and coherence by:

defining which connections exist

defining when they open

defining what may pass through them

There are no exceptions.

3. The Gate Chain (Canonical)

All information flow in A7DO must follow this chain:

World
  ↓
PerceptGate
  ↓
Mind
  ↓
FrameGate
  ↓
Accountant
  ↓
MemoryGate
  ↓
Memory
  ↓
ConsolidationGate
  ↓
Embodiment
  ↓
ExpectationGate
  ↓
Mind
  ↓
ExpressionGate
  ↓
World / UI

No subsystem may bypass a gate.
No subsystem may write “upstream”.

4. PerceptGate

World → Mind

Purpose

Convert raw world interactions into bounded percepts.

Input

world events (contact, pressure, temperature, motion)

outcome signals (blocked, resolved, success/fail)

Output

percepts with no semantics:

pressure_delta

temperature_delta

nociception

effort

motion_vector

contact_flag

Opening condition

event source is world

sensor channel exists

embodiment constraints allow (e.g. thermal only when contact)

Key property

Percepts cannot reference:

memory

identity

future states

They are purely present-moment signals.

5. FrameGate

Mind → Accountant

Purpose

Define frame boundaries.

This gate is the replacement for time.

Input

percepts

actions

outcomes

internal regulatory signals

Output

closed frames

subframes (when fragmentation occurs)

Opening condition

The gate closes a frame when:

information flow drops below noise

resolution occurs

fragmentation threshold is exceeded

overload forces segmentation

Key property

Frames close because information ends, not because time passes.

6. MemoryGate

Accountant → Memory

Purpose

Allow pattern formation, not raw storage.

Input

AccountantEntry only

Output

MemoryTrace

cluster updates

Opening condition

frame is closed

accountant entry is structurally valid

Key property

Memory cannot see:

raw events

percept streams

actions

This prevents memory poisoning and hallucinated knowledge.

7. ConsolidationGate

Memory → Embodiment

Purpose

Turn repeated, stable patterns into embodied knowledge.

Input

MemoryCandidate only

Output

LedgerEntry (new or revision)

or BLOCK / DEFER decision

Opening condition

All structural thresholds must be met:

sufficient support

sufficient repetition

stability above threshold

locality is clear

no strong contradiction with existing ledger entries

Key property

Embodiment cannot be written by thought, language, or instruction.
Only lived repetition can open this gate.

8. ExpectationGate

Embodiment → Mind

Purpose

Provide anticipatory bias, not commands.

Input

LedgerEntries

Output

expectations such as:

likely boundary

likely thermal response

likely resolution pattern

Opening condition

current context matches ledger constraints

Key property

Expectations influence prediction, not action selection.

This prevents goal lock-in.

9. ExpressionGate

Mind → World / UI

Purpose

Allow action and communication.

Input

actions

utterance tokens

attention shifts

Output

world actions

UI or chat output

Opening condition

channel exists

world allows the action (e.g. not blocked)

Key property

Expression cannot directly access memory or embodiment.

All output is mediated by the mind state.

10. Safety by Structure

Because of gates:

No reward hacking is possible (no reward gate exists)

No belief injection is possible (no embodiment write gate exists)

No temporal pressure exists (no time variable exists)

No runaway loops exist (frames must close)

No shortcut learning exists (experience must recur)

Safety is not enforced.
It is emergent from structure.

11. Relationship to Sandy’s Law

Under Sandy’s Law:

dynamics are governed by structure

transitions occur at information thresholds

stability emerges from constrained flow

Gates are the local implementation of Sandy’s Law in cognition.

They replace:

rules

permissions

safety policies

With:

physically grounded couplings

12. Summary

Gates are connections, not rules.

Information can only move where structure allows.

Every subsystem is isolated by default.

Development cannot be rushed or bypassed.

If a gate does not exist, the system cannot cheat.

This file defines the full information topology of A7DO.
All implementations must conform to it.