# Cycle 3 — Causality Specification
# Time, Causality & Irreversibility Layer
# Date: 2026-03-02  |  Author: Kanishk Singh

---

## 1. Purpose

The Time, Causality & Irreversibility Layer (TCIL) is the third and final
primitive of the Quantum Architecture Foundations system. It provides:

- **Strict causal ordering** of all events produced by Cycles 1 and 2
- **Irreversibility enforcement** — events cannot be deleted or modified
- **Compensation primitives** — the only sanctioned way to correct errors
- **Point of No Return (PONR) markers** — seals that permanently prevent
  compensation of historical events

---

## 2. Quantum Alignment

### 2.1 Causality in Quantum Systems

The quantum no-signaling theorem prohibits faster-than-light signaling —
including backwards-in-time causation. Measurement outcomes cannot retroactively
change the past. This layer enforces the classical analogue:

> Events form a strict partial order. No event can be placed before a committed
> predecessor. No committed event can be erased.

### 2.2 Why Rollback Violates Causality

Rollback would require the system to "un-cause" an event. If event E2 was
caused by E1, rolling back E1 would invalidate E2's causal justification.
But E2 already happened — its effects propagated. Rollback creates a
**forked timeline**, which is architecturally equivalent to hidden global state.

The correct response to an erroneous event is **compensation** — a new event
that corrects the downstream effects without pretending the original never happened.

### 2.3 Time Arrow

The LogicalClock always increments. The clock value is a Lamport logical clock,
not wall time. It provides total causal ordering within a single timeline instance.
Cross-timeline ordering (distributed systems) requires a vector clock extension
— this is documented as a non-guarantee.

---

## 3. Primitive Definitions

### 3.1 LogicalClock

```
tick() → int    (increment and return new value)
peek() → int    (read current value, no-op)
```

Property: `tick()` always returns a value strictly greater than the previous `tick()`.
No method exists to decrease or reset the clock.

### 3.2 CausalEvent

| Field | Type | Constraint |
|---|---|---|
| causal_id | int | ≥ 0; produced by LogicalClock.tick() |
| event_type | str | non-empty tag |
| payload | object | any (should be frozen) |
| predecessor_id | int or None | must be < causal_id |
| wall_time_ns | int | physical wall clock at creation |
| is_compensation | bool | True if this corrects a prior event |

CausalEvent is a **frozen dataclass** — immutable after creation.

### 3.3 CausalLink

Directed edge: cause_id → effect_id. Constraint: cause_id < effect_id.

### 3.4 PointOfNoReturn

A permanent seal placed at a specific causal_id. After sealing:
- All events with causal_id ≤ sealed_id are **permanently non-compensable**
- New events can still be added after the seal point
- The PONR marker itself is a frozen record

---

## 4. Causality Guarantees

| ID | Guarantee |
|---|---|
| C1 | causal_id values are strictly monotonically increasing |
| C2 | predecessor_id of event[i] is always causal_id of event[i-1] |
| C3 | CausalEvent objects are frozen — field mutation is rejected |
| C4 | CausalTimeline has no delete, rollback, or revert methods |
| C5 | Compensation adds a new event — it never modifies the original |
| C6 | PONR seals cannot move backwards (sealed_up_to only advances) |
| C7 | Compensating a sealed event raises PointOfNoReturnViolationError |

---

## 5. Irreversibility Guarantees

1. No CausalEvent is ever removed from the timeline log.
2. No CausalEvent field can be changed after creation.
3. Compensation produces a NEW event with `is_compensation=True`.
4. The original event is still in the log alongside its compensation.
5. PONRs are final — a sealed region cannot be re-opened.

---

## 6. Non-Guarantees

1. The TCIL does NOT provide distributed consistency across multiple
   CausalTimeline instances. Cross-instance ordering is out of scope.
2. The TCIL does NOT provide wall-clock accuracy or global time.
   `wall_time_ns` is advisory only — trust logical ordering, not wall time.
3. The TCIL does NOT prevent semantically invalid events from being recorded.
   Semantic validation is the caller's responsibility.
