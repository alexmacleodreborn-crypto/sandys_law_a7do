Memory
Pattern Formation Without Time or Belief
1. Definition

Memory in A7DO is a pattern-forming system, not a storage system.

Memory does not:

store events

store facts

store symbols

store beliefs

Memory does:

compare closed frames

detect recurrence

measure similarity

form pattern clusters

propose consolidation into embodiment

Memory operates only on completed frames.

2. Why Memory Does Not Store Events

Raw events are:

high volume

noisy

context-dependent

unsafe to reason over directly

A7DO already stores events in an append-only event log for auditing and replay.

Memory sits above that log and only receives structured summaries (AccountantEntries).

This separation prevents:

hallucinated knowledge

false certainty

semantic drift

self-reinforcing errors

3. Inputs to Memory

Memory receives information only through the MemoryGate.

Allowed input

AccountantEntry (one per closed frame)

Forbidden input

raw events

percept streams

actions

world state

language

embodiment data

If an input does not arrive as an AccountantEntry, Memory cannot see it.

4. MemoryTrace

For each AccountantEntry, Memory creates a MemoryTrace.

A MemoryTrace is a normalized representation of an episode.

MemoryTrace contains:

signature keys

numeric feature vector

active body regions

stability classification

support weight

MemoryTrace is immutable.

5. Similarity and Recognition

Memory defines similarity structurally, not symbolically.

Similarity is computed using:

numeric feature similarity

body-region overlap

key-family overlap

Memory can therefore distinguish:

same
(high similarity across all dimensions)

similar
(shared structure with differences)

seen before but not the same
(shared family, different manifestation)

novel
(no meaningful similarity)

This is the basis of recognition without concepts.

6. PatternClusters

Memory groups related traces into PatternClusters.

A PatternCluster represents a recurring class of experience.

Each cluster tracks:

centroid feature profile

region activation profile

accumulated support

internal variance

stability measure

Clusters evolve gradually as new traces arrive.

No cluster is ever created from a single frame.

7. Stability

Stability measures how consistent a pattern is across experiences.

A cluster is stable when:

internal variance is low

member similarity remains high

resolution tends to occur

overload does not dominate

Stability is not confidence.
It is structural consistency.

8. Novelty and Familiarity

Memory provides two signals downstream:

Familiarity
How closely a new trace matches existing clusters

Memory Novelty
The inverse of familiarity

These signals allow the system to:

recognize recurring situations

detect new situations

prioritize investigation without reward

9. Memory Does Not Decide

Memory does not:

choose actions

select goals

enforce behavior

modify embodiment

Memory only proposes.

All decisions about permanence are deferred to the Consolidation Gate.

10. MemoryCandidates

When a PatternCluster becomes sufficiently:

repeated

supported

stable

localized

Memory emits a MemoryCandidate.

A MemoryCandidate is a proposal that:

“This pattern may represent a stable property of the world or body.”

MemoryCandidates are sent only to the ConsolidationGate.

11. What Memory Can Learn Early

Before language or objects, Memory can form patterns such as:

repeated resistance at the same body region

recurring thermal responses under contact

scuttling sequences that resolve constraints

overload patterns that fragment frames

settling patterns that reduce prediction error

These are pre-conceptual memories.

12. Safety Properties

Because of its design, Memory cannot:

invent facts

overwrite embodiment

escalate certainty

inject beliefs

reason about the future

Memory only accumulates evidence.

Knowledge must be earned by repetition.

13. Relationship to Frames and Embodiment

Frames define episodes

Memory detects recurrence

Embodiment records invariants

Memory is the bridge between experience and knowledge.

Without Memory:

nothing stabilizes

Without Embodiment:

nothing becomes permanent

14. Summary

Memory forms patterns, not facts

Memory operates only on closed frames

Memory proposes, it does not enforce

Recognition emerges without symbols

Knowledge requires repetition and stability

Memory remembers structure, not stories.

This file defines the complete doctrine of memory in A7DO.