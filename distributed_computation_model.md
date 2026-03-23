# Distributed Computation Model

**System:** Quantum Foundation — Distributed Computation Layer  
**Date:** 2026-03-23  
**Authors:** Vinayak (Validation Lead), Raj Prajapati (Enforcement Gateway), Sankalp (Intelligence Layer)  
**Status:** SEALED — Builds on Cycles 1–8 core without modification  

---

## 1. System Overview

This model describes deterministic distributed computation over the Quantum Foundation system.  
The existing `FullStackHarness` (Cycles 1–8) remains the sealed computation kernel.  
The distributed layer adds: multi-node coordination, partial state sharing, ordered execution, divergence handling, and reconciliation.

```
┌──────────────────────────────────────────────────────────┐
│                      NetworkHub                          │
│  (Global causal sequencer — single source of ordering)  │
└──────────┬───────────────┬──────────────────┬───────────┘
           │               │                  │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌────────▼──────┐
    │   Node A    │ │   Node B    │ │    Node C     │
    │FullStack    │ │FullStack    │ │ FullStack     │
    │ Harness     │ │ Harness     │ │ Harness       │
    │ + Partial   │ │ + Partial   │ │ + Partial     │
    │ State Store │ │ State Store │ │ State Store   │
    └─────────────┘ └─────────────┘ └───────────────┘
```

---

## 2. Computation Step Definition

A **computation step** is an atomic, irreversible, causally-ordered transformation applied uniformly across all nodes.

### Formal Definition

```
ComputationStep := {
  causal_id     : ℕ₊         # Strictly increasing, assigned by Hub
  origin_node   : NodeID      # Node that proposed the step
  step_type     : EVOLVE | MEASURE | SYNC
  payload       : StepPayload # Type-specific parameters
  timestamp     : ISO8601     # Wall-clock at proposal time (non-authoritative)
}
```

### Step Types

| Type | Trigger | Effect | Reversible? |
|------|---------|--------|-------------|
| `EVOLVE` | Node proposes unitary rule | Advances quantum state via registered operator | No (one-way causal chain) |
| `MEASURE` | Node proposes collapse | Collapses state with deterministic seed | No (irreversible by physics) |
| `SYNC` | Hub injects | Forces state-hash comparison across all nodes | No side-effect on state |

### Causal Ordering Rule

> **Every node applies steps in strictly increasing `causal_id` order.  
> A step with `causal_id = N` is never applied before `causal_id = N-1` is committed.**

---

## 3. Message Structure Between Nodes

All inter-node communication flows through the `NetworkHub`. Nodes do not talk directly.

### 3.1 ProposalMessage (Node → Hub)

```python
@dataclass(frozen=True)
class ProposalMessage:
    proposal_id  : str     # UUID from proposing node (pre-sequencing identifier)
    origin_node  : str     # Node ID
    step_type    : str     # "EVOLVE" | "MEASURE" | "SYNC"
    payload      : dict    # {"rule_name": str} | {"token_id": str, "seed": int} | {}
    proposed_at  : float   # monotonic timestamp
```

### 3.2 SequencedEvent (Hub → All Nodes)

```python
@dataclass(frozen=True)
class SequencedEvent:
    causal_id    : int     # Global sequence number, Hub-assigned
    proposal_id  : str     # Echoed from ProposalMessage for traceability
    origin_node  : str
    step_type    : str
    payload      : dict
    sequenced_at : float   # Hub timestamp at sequencing
```

### 3.3 AckMessage (Node → Hub, optional)

```python
@dataclass(frozen=True)
class AckMessage:
    causal_id    : int
    node_id      : str
    state_hash   : str     # SHA-256 of node state after applying event
    ack_type     : str     # "APPLIED" | "BUFFERED" | "REJECTED"
```

### 3.4 SyncReport (Hub → Coordinator, on SYNC step)

```python
@dataclass(frozen=True)
class SyncReport:
    causal_id    : int
    node_hashes  : dict    # {node_id: state_hash}
    consensus    : bool    # True if all hashes equal
    diverged_nodes: list   # Nodes with mismatched hashes
```

---

## 4. Partial State Sharing Protocol

Nodes maintain **full local state** (replica architecture) but may expose **partial views** to peers for diagnostic, catch-up, and reconciliation purposes.

### 4.1 What "Partial State" Means

A node holds:
- `committed_state`: last fully applied `FullStackHarness` state (authoritative)
- `pending_buffer`: events received but not yet causally applicable (out-of-order)
- `state_snapshot`: a point-in-time hash + amplitude dict for export

A partial state export is **read-only**. No node may mutate another node's state.

### 4.2 Sharing Rules

| Rule | Description |
|------|-------------|
| **Read Only** | State exports are snapshots. They cannot trigger mutations. |
| **Causal Stamp** | Every exported snapshot carries the `last_applied_causal_id` |
| **Hash-Only Comparison** | For consensus checks, only hashes are compared, not raw amplitudes |
| **Catch-Up Only** | A lagging node may request the event log from Hub, not peer state |

---

## 5. Deterministic Merge Guarantee

When a node catches up from buffered or replayed events:

```
merge(committed_state, buffered_events) → new_committed_state
```

The merge is deterministic because:
1. Events are applied strictly in `causal_id` order
2. Each `FullStackHarness._apply_event()` is a pure function given the same input
3. No random or time-based elements enter the computation kernel (seed is always explicit)
4. Hub is the single sequencer — no event receives two different `causal_id` values

**Theorem:** For any node N, if it receives the complete event log from `causal_id=1` to `causal_id=K`, starting from the same initial state, it will produce an identical `state_hash` as any other node that processed the same log.

---

## 6. Authority Model

| Entity | Authority |
|--------|-----------|
| `NetworkHub` | Sole authority on causal ordering. Assigns all `causal_id`s. |
| `DistributedStateNode` | Sole executor on local state. No node can write to another. |
| `FullStackHarness` | Sole enforcer of physical invariants (Cycles 1–8). |
| Coordinator (client) | Proposes operations. Has zero authority over sequencing. |

**Raj Prajapati — Enforcement Gateway Boundary:** No node may leak state authority to another. The Hub may only pass `SequencedEvent` objects — never raw state mutations.

---

## 7. Failure and Divergence Taxonomy

| Failure Type | Example | System Response |
|-------------|---------|----------------|
| **Delayed delivery** | Node A receives event 3 seconds late | Buffer → apply in order → no divergence |
| **Missing event** | Node B never receives `causal_id=7` | Buffer stalls; Hub detects via SYNC; reconciliation triggered |
| **Out-of-order** | Node C gets `causal_id=9` before `causal_id=8` | Buffered until 8 arrives |
| **Duplicate event** | Node A receives `causal_id=5` twice | Second copy silently dropped (already committed) |
| **Invalid event** | Malformed payload or non-unitary operator | `FullStackHarness` rejects; node raises `InvariantViolationError` |
| **Consensus failure** | Nodes disagree on final hash | `SYNC` step detects; system halts; reconciliation required |

---

## 8. Integration Points (Sankalp — Intelligence Layer)

The reasoning/intelligence layer may observe the system through:
- `node.observe()` → read-only amplitude dict (no side effects)
- `node.get_state_hash()` → deterministic hash without altering state
- `hub.get_event_log()` → complete ordered event history

The intelligence layer **may not**:
- Propose operations without going through Hub
- Modify event payloads
- Access `FullStackHarness` internals directly

---

## 9. Deliverables Summary

| Module | Role |
|--------|------|
| `distributed_state_propagation.py` | Extended node with partial state and merge logic |
| `computation_protocol.py` | Proposal → Sequencing → Execution protocol |
| `divergence_simulation.py` | Controlled divergence scenarios |
| `reconciliation_engine.py` | Catch-up and deterministic replay |
| `distributed_invariant_check.py` | Global invariant consensus enforcement |
| `distributed_computation_demo.py` | Full end-to-end 3+ node simulation |

---

*Model sealed. Cycles 1–8 core untouched. All new behavior is additive.*
