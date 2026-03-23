# Reconciliation Report

**System:** Quantum Foundation — Distributed Computation Layer  
**Phase:** 5 — Deterministic Reconciliation  
**Date:** 2026-03-23  
**File:** `reconciliation_engine.py`  

---

## Overview

This report documents the deterministic reconciliation mechanism that brings lagging nodes back into consensus with the network. Reconciliation guarantees:

1. **Same final hash** — all nodes produce an identical state hash
2. **No duplicate application** — events already committed are skipped
3. **No state overwrite** — all changes flow through `FullStackHarness` transitions
4. **Causal order preserved** — events applied strictly by `causal_id`

---

## ReconciliationEngine Protocol

```
Identify reference node (highest committed causal_id)
For each lagging node:
    Fetch missing events from Hub event log (from committed_id+1 to ref_id)
    Filter out SYNC events (no state effect)
    Apply in strict causal order via receive_event()
    Skip events already committed (causal_id < next_expected)
    Verify final hash == reference hash
Report convergence
```

---

## Test Case: Node B Missing Event 2

### Setup

| Event | Step | Delivered To |
|-------|------|-------------|
| 1 | EVOLVE H | All nodes |
| 2 | EVOLVE X | Node A, Node C (Node B excluded) |
| 3 | EVOLVE H | All nodes (Node B buffers — waiting for event 2) |

### Pre-Reconciliation State

| Node | Committed ID | Hash | Partial? |
|------|-------------|------|----------|
| Node_A | 3 | `<ref>` | No |
| Node_B | 1 | `<stale>` | **Yes** (event 3 buffered) |
| Node_C | 3 | `<ref>` | No |

### Reconciliation Steps (Node B)

| Step | Action | Result |
|------|--------|--------|
| 1 | Identify reference: Node_A (committed_id=3) | Reference hash captured |
| 2 | Fetch missing events: causal_id 2..3 from Hub | 2 events retrieved |
| 3 | Filter SYNC events | None to filter |
| 4 | Apply causal_id=2 (EVOLVE X) | Applied. Buffer flushes → causal_id=3 also applied |
| 5 | Verify hash | Post hash == reference hash ✓ |

### Post-Reconciliation State

| Node | Committed ID | Hash | Converged? |
|------|-------------|------|-----------|
| Node_A | 3 | `<hash>` | — (reference) |
| Node_B | 3 | `<hash>` | **Yes ✓** |
| Node_C | 3 | `<hash>` | Yes ✓ |

**Full consensus reached:** True

---

## Duplicate Event Guard

The engine skips events with `causal_id < node.next_expected_causal_id`. This is verified in `NodeReconciliationResult.events_already_committed`. An event replayed twice will be silently skipped — **no double-application ever occurs**.

---

## Determinism Guarantee

The reconciliation outcome is deterministic because:

1. Events are sorted by `causal_id` before replay
2. `receive_event()` delegates to `FullStackHarness._apply_event()` — a pure function
3. No wall-clock time, random seed, or network latency enters the computation
4. The Hub is the sole source of the authoritative event log

**Theorem:** Any node that processes the full event log from `causal_id=1..K` starting from the same initial state will produce the same `state_hash` as any other node that processed the same log.

---

## System Halt on Reconciliation Failure

If a replayed event is rejected by `FullStackHarness` (e.g., non-unitary operator, norm violation), the reconciliation record will include `error` and `converged=False`. The caller should treat this as an irrecoverable condition and halt the node.

---

## Full Reconciliation Report Fields

| Field | Meaning |
|-------|---------|
| `reference_node` | Most advanced node used as convergence target |
| `reference_causal_id` | Authoritative causal position |
| `reconciled_nodes` | Per-node reconciliation results |
| `full_consensus_reached` | True if all nodes share identical hash at same causal ID |
| `hash_matches` | Per-node convergence boolean |

---

*Generated from `reconciliation_engine.py` — Phase 5, Quantum Foundation Distributed Computation System*
