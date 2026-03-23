# Divergence Report

**System:** Quantum Foundation — Distributed Computation Layer  
**Phase:** 4 — Controlled Divergence Simulation  
**Date:** 2026-03-23  
**File:** `divergence_simulation.py`  

---

## Overview

This report documents three controlled divergence scenarios simulated against the distributed quantum foundation node network. Each scenario demonstrates that the system correctly **detects** divergence without breaking state integrity or crashing.

---

## Scenario A — Delayed Node

**Description:**  
Node A does not receive events 1 and 2. Nodes B and C advance normally. A SYNC step is issued with only B and C participating.

**Setup:**
- Events 1 and 2 are `delay_nodes=["Node_A"]` — held at Hub, not delivered
- Node B and Node C receive and apply both events
- SYNC issued — Node A excluded

**Observations:**

| Node | Committed causal_id | Hash matches B/C? | Partial? |
|------|---------------------|-------------------|----------|
| Node_A | 0 (initial) | No | No (no pending) |
| Node_B | 2 | — (reference) | No |
| Node_C | 2 | Yes | No |

**Result:** `DIVERGED (detected)`  
Node A holds an older state. Its hash diverges from B and C. The system did not crash — Node A's local state is physically valid at its own causal position.

**Recovery Path:** Release held events → Node A receives causal_id=1 and causal_id=2 → buffer flushes → Node A catches up.

---

## Scenario B — Missing Event

**Description:**  
Node B permanently misses `causal_id=2` (the X gate). It receives events 1 and 3, but causal_id=3 is buffered waiting for causal_id=2.

**Setup:**
- Event 1: all nodes receive
- Event 2: `exclude_nodes=["Node_B"]` — never delivered
- Event 3: all nodes receive (Node B buffers it)

**Observations:**

| Node | Committed causal_id | Pending | Hash matches A? | Partial? |
|------|---------------------|---------|-----------------|----------|
| Node_A | 3 | — | — (reference) | No |
| Node_B | 1 | [3] | No | **Yes** |
| Node_C | 3 | — | Yes | No |

**Result:** `DIVERGED (detected)`  
Node B is permanently stuck at causal_id=1. Event 3 is in its buffer but cannot be applied because causal_id=2 is missing. SYNC detects the hash discrepancy.

**Recovery Path:** Hub replays causal_id=2 to Node B → buffer flushes → Node B applies events 2 and 3 → converges with A and C.

---

## Scenario C — Out-of-Order Delivery

**Description:**  
Node C receives causal_id=3 before causal_id=2 (out-of-order network delivery). The event is buffered deterministically.

**Setup:**
- Event 1: all receive
- Event 2: `delay_nodes=["Node_C"]` — held at Hub
- Event 3: all receive (including Node C — buffered waiting for 2)
- Release event 2 → buffer flushes → Node C applies 2, then 3

**Observations (before release):**

| Metric | Value |
|--------|-------|
| Node_C is_partial | True |
| Node_C pending | [3] |
| Node_C committed_id | 1 |

**Observations (after release):**

| Metric | Value |
|--------|-------|
| Node_C is_partial | False |
| Node_C committed_id | 3 |
| Consensus (A=B=C) | **True** |

**Result:** `STABLE (no permanent divergence)`  
Out-of-order delivery is automatically resolved by the causal buffer mechanism. The system correctly waited for causal_id=2 before applying causal_id=3. No state corruption. No manual intervention needed.

---

## Summary Table

| Scenario | Type | Diverged? | System Crash? | Recovery |
|----------|------|-----------|---------------|----------|
| A — Delayed Node | Delayed delivery | Yes | No | Release held events |
| B — Missing Event | Permanently dropped | Yes | No | Hub replays missing event |
| C — Out-of-Order | Network reordering | Temporary | No | Automatic (buffer flush) |

---

## Invariant Compliance

In all three scenarios:
- **No invariant was violated** at the local node level (each node's state was physically valid at its own causal position)
- **Global invariant check** correctly emitted `system_should_halt=True` for scenarios A and B
- **Cycle 1–8 core was not modified** — the sealed logic correctly rejected any attempt to apply events out of order

---

*Generated from `divergence_simulation.py` — Phase 4, Quantum Foundation Distributed Computation System*
