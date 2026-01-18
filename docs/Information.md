Phase 0 — World Integrity (Milestone 0)

Implement:

world/space.py

world/physics.py

world/sensors.py

world/actuators.py

Stop condition:
Identical actions → identical event sequences.

Phase 1 — Frames (Milestone 1)

Implement:

frames/frame.py

frames/frame_store.py

frames/fragment.py

Stop condition:
All events belong to closed frames.

Phase 2 — Accounting (Milestone 2)

Implement:

accounting/accountant.py

accounting/metrics.py

accounting/prediction_error.py

Stop condition:
Frames → stable AccountantEntries.

Phase 3 — Memory (Milestone 3)

Implement:

memory/trace.py

memory/similarity.py

memory/clustering.py

memory/decay.py

Stop condition:
Clusters form only after repetition.

Phase 4 — Embodiment (Milestone 4)

Implement:

embodiment/ledger.py

embodiment/boundaries.py

embodiment/thermal_pain.py

Stop condition:
Prediction error decreases without instruction.

Phase 5 — Scuttling (Milestone 5)

Implement:

scuttling/body_map.py

scuttling/motor_patterns.py

scuttling/skill_stability.py

Stop condition:
Movement reduces load and improves resolution.

Phase 6 — Regulation & Mind (Milestone 6–7)

Implement:

mind/regulation.py

mind/coherence.py

mind/perception.py

mind/preference.py

Stop condition:
Confidence floor rises, no oscillation.

Phase 7 — Education (Milestone 8–9)

Implement:

education/curriculum.py

education/exams.py

education/cv.py

Stop condition:
Performance stable across contexts.

Phase 8 — Roles (Milestone 10)

Implement:

roles/base_role.py

roles/sled_interface.py

roles/system_manager.py

Stop condition:
External work does not destabilize system.

III. Visual Diagrams (Text-Canonical)

These are doctrine diagrams — they map 1:1 to code.

1. Frame Flow (No Time)
World Events
     ↓
[ Frame Opens ]
     ↓
Information Accumulates
     ↓
Resolution / Silence / Fragmentation
     ↓
[ Frame Closes ]
     ↓
Accountant Entry

2. Layer Flow (No Downwrites)

World
  ↓
Frames
  ↓
Accounting
  ↓
Memory
  ↓
Embodiment
  ↓
Scuttling
  ↓
Mind
  ↓
Education
  ↓
Roles
(No arrows upward. Ever.)

3. Collapse vs Coherence

Unresolved Info → Accumulation → Collapse

Resolved Info → Embodiment → Coherence → Stability

4. Why This System Is Dangerous (and Valuable)

Most systems:

Scale ↑ → Complexity ↑ → Collapse


A7DO:

Scale ↑ → Constraints ↑ → Coherence ↑


That inversion is rare.