# Sovereign Quantum Architecture Primitives
# Kanishk Singh — Foundations Phase
# Version: 1.0.0 | Date: 2026-03-02

---

## Overview

This repository contains the foundational quantum-aligned architecture
primitives built across three sealed cycles. The system treats **uncertainty,
state evolution, measurement, collapse, time, and irreversibility** as
first-class architectural constraints.

The primitives are hardware-agnostic: they remain valid when classical
backends are replaced by real quantum hardware.

---

## Repository Structure

```
quantum_foundation/
├── cycle1/                          # Sovereign State Evolution Engine
│   ├── state_evolution_engine.py    # Core engine
│   ├── invariants.py                # I1–I7 machine-checkable invariants
│   ├── tests/
│   │   ├── test_deterministic_replay.py
│   │   └── test_abuse.py
│   └── docs/
│       ├── architecture_spec.md
│       └── handover.md
│
├── cycle2/                          # Deterministic Measurement & Collapse
│   ├── measurement_policy.py        # ProjectiveMeasurementPolicy, WeakMeasurementPolicy
│   ├── collapse_engine.py           # CollapseEngine + IrreversibleCollapseEvent
│   ├── invariants.py                # M1–M7 machine-checkable invariants
│   ├── tests/
│   │   └── test_collapse.py
│   └── docs/
│       └── measurement_spec.md
│
├── cycle3/                          # Time, Causality & Irreversibility
│   ├── causality_primitives.py      # LogicalClock, CausalEvent, CausalLink, PONR
│   ├── timeline.py                  # CausalTimeline (append-only)
│   ├── integration.py               # QuantumFoundationSystem (all 3 wired)
│   ├── tests/
│   │   ├── test_causality.py
│   │   └── test_irreversibility.py
│   └── docs/
│       ├── causality_spec.md
│       └── coherence_proof.md
│
├── integration_demo.py              # End-to-end demonstration
├── README.md                        # This file
├── INVARIANTS.md                    # Master invariant index (all cycles)
└── HANDOVER.md                      # Handover notes for reviewers
```

---

## Core Prohibitions (Enforced Architecturally)

| Prohibition | Enforced By |
|---|---|
| No execution authority | TransitionRule is a pure function only |
| No hidden global state | All state held in engine instances |
| No retroactive mutation | Frozen dataclasses + append-only logs |
| No rollback | No delete/revert/undo methods exist |
| No black-box logic | Every transition registered and named |
| No unregistered observation types | Rejected at `observe()` before any rule runs |
| No measurement without token | `CollapseToken` required for every collapse |

---

## Running the Tests

Requires Python 3.9+ (stdlib only — no pip dependencies).

```bash
# From the quantum_foundation root:

# All tests
python -m unittest discover -s cycle1/tests -v
python -m unittest discover -s cycle2/tests -v
python -m unittest discover -s cycle3/tests -v

# End-to-end integration demo
python integration_demo.py
```

---

## Quick Concept Map

```
Observation ──▶ SovereignStateEngine ──▶ StateDelta
                      │                      │
                      │ current_state         │
                      ▼                      ▼
              CollapseEngine ◀──── (StateVector snapshot)
              [CollapseToken]
                      │
                      ▼
           IrreversibleCollapseEvent
                      │
                 Both recorded ▼
              CausalTimeline (append-only, ordered)
                      │
                 [PointOfNoReturn seals regions]
```

---

## Cycle Summaries

| Cycle | What it does | Key type |
|---|---|---|
| 1 | State evolves under observations | `SovereignStateEngine` |
| 2 | State is measured, information is declared lost | `CollapseEngine` |
| 3 | All events are causally ordered and sealed | `CausalTimeline` |
-=-=-=-