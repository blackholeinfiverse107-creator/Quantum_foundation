# Cycle 1 — Architecture Specification
# Sovereign State Evolution Engine
# Date: 2026-03-02  |  Author: Kanishk Singh

---

## 1. Purpose

The Sovereign State Evolution Engine (SSEE) is the foundational primitive of
the Quantum Architecture Foundations system. Its single responsibility is to
evolve a quantum-aligned state representation in response to typed observations,
using only explicit transition rules, while maintaining a tamper-evident,
append-only history of all state changes.

The SSEE is **not** an executor, **not** an orchestrator, and **not** a
decision maker. It is a pure state machine for state that lives in superposition.

---

## 2. Quantum Alignment

### 2.1 State vs Observable

A quantum system's **state** (the wavefunction ψ) is fundamentally different
from any **observable** (a measurement outcome). The SSEE models this by:

- `StateVector` ≡ ψ — internal, not directly observable from outside
- `Observation` ≡ a classical input event, not a measurement of ψ
- State evolution ≡ unitary-like transformation: deterministic, norm-preserving

The engine does **not** perform measurement. Measurement belongs to Cycle 2.

### 2.2 State Evolution Without Observation (of State)

In quantum mechanics, state evolves according to the Schrödinger equation even
without external measurement. The SSEE models controlled evolution: only
registered `TransitionRule` functions may alter state, and each rule must
preserve the unit norm of the `StateVector`.

### 2.3 No-Cloning Intuition

The StateVector is a value object — it is copied on every transition (prior_state
and next_state are distinct instances). The engine does not support shared
references to mutable state. This models the no-cloning principle: the "full"
internal state cannot be duplicated by external actors.

### 2.4 Irreversibility as a Rule

Once a `StateDelta` is appended to the log, it cannot be removed or modified.
The prior_state recorded in each delta is a frozen snapshot. This models
quantum irreversibility: observing a transition event makes it a permanent part
of the causal record.

---

## 3. Component Definitions

### 3.1 `Observation`
| Property | Type | Constraint |
|---|---|---|
| observation_type | str | Non-empty; must match a registered rule |
| payload | tuple | Immutable; content validated by the rule |

An Observation carries no execution semantics. It is a typed information token.

### 3.2 `StateVector`
| Property | Constraint |
|---|---|
| amplitudes | Tuple of Amplitude objects (frozen) |
| norm | Must equal 1.0 ± 1e-10 (Born rule pre-condition) |
| dimension | Fixed at engine initialization; never changes |
| Zero vector | FORBIDDEN — raises ValueError on construction |

StateVector is constructed once and never mutated. All operations return new
StateVector instances.

### 3.3 `TransitionRule`
```
type TransitionRule = (StateVector, Observation) -> StateVector
```
A TransitionRule is a **pure function**:
- No side effects
- No external state access
- No execution of commands
- Must return a valid StateVector of the same dimension

### 3.4 `StateDelta`
| Property | Constraint |
|---|---|
| sequence_number | Strictly increasing integer ≥ 0 |
| prior_state | Frozen StateVector before transition |
| next_state | Frozen StateVector after transition |
| observation | The Observation that triggered this delta |
| applied_rule | Name of the TransitionRule applied |
| timestamp_ns | Wall-clock time in nanoseconds (monotonic) |

StateDelta is a frozen dataclass — it cannot be mutated after creation.

### 3.5 `SovereignStateEngine`
- Owns the registry of TransitionRules
- Holds current StateVector (private, read-only property)
- Maintains the `_ImmutableDeltaLog`
- Exposes `observe(obs)` → `StateDelta`
- Exposes `replay_from_log(initial, log)` → `StateVector`
- Has **no** public state setter

---

## 4. Invariants (Summary)

| ID | Name | Type | Description |
|---|---|---|---|
| I1 | Norm Conservation | GUARANTEE | ‖ψ‖² = 1 at all times |
| I2 | No Zero Vector | FORBIDDEN STATE | Zero vector is not a valid state |
| I3 | History Immutability | GUARANTEE | Delta log is append-only, never mutated |
| I4 | Sequence Monotonicity | GUARANTEE | Seq numbers strictly increase by 1 |
| I5 | Delta Continuity | GUARANTEE | next_state[i] == prior_state[i+1] |
| I6 | Dimension Preservation | IMPOSSIBLE TRANSITION | Hilbert space dim is fixed |
| I7 | Replay Determinism | GUARANTEE | Same input → same final state |

Full invariant proofs are in `invariants.py`.

---

## 5. Forbidden States

1. **Zero vector** — all amplitudes zero. No physical meaning.
2. **Unnormalized state** — ‖ψ‖ ≠ 1. Probabilities undefined.
3. **Empty state** — no basis states. Undefined Hilbert space.
4. **Dimension-changed state** — different number of basis labels than initial.

---

## 6. Impossible Transitions

1. **Unregistered observation type** → immediately rejected at `observe()`
2. **Rule returning non-StateVector** → rejected post-rule, pre-commit
3. **Rule changing dimension** → rejected post-rule, pre-commit
4. **Duplicate rule registration** → rejected at `register_rule()`
5. **Sequence number out of order** → rejected at `_ImmutableDeltaLog.append()`

---

## 7. Guarantees

1. Every state transition is traceable to exactly one registered rule and one Observation.
2. The delta log forms a complete, replay-able history of the engine's lifetime.
3. Replaying the delta log from the initial state always produces the current state.
4. No external actor can modify state or history without calling `observe()`.

---

## 8. Non-Guarantees (Explicitly Declared)

1. The engine does NOT perform measurement — that is Cycle 2.
2. The engine does NOT order events across multiple concurrent instances — that is Cycle 3.
3. The engine does NOT validate the semantic meaning of observation payloads.
4. The engine does NOT prevent two different paths from converging on the same state.
5. The engine does NOT guarantee that rules are physically realizable on quantum hardware —
   only that they preserve the mathematical invariants.

---

## 9. Design Rationale

**Why frozen dataclasses?**
Python frozen dataclasses enforce immutability at the language level. Any attempt
to set an attribute raises `FrozenInstanceError`. This is not a convention — it is
mechanically enforced.

**Why pure functions for TransitionRules?**
A pure function has no observable effect other than its return value. This
eliminates the possibility of hidden side-effects (file I/O, network calls,
global state mutation) inside a rule. The rule can be tested in total isolation.

**Why a private `_ImmutableDeltaLog`?**
The log is not publicly accessible for appending. The only way to add entries
is via `observe()`, which enforces all invariants before appending. Exposing
the log directly would allow external append or modification.

**Why no rollback?**
Rollback would require deleting or overwriting delta entries, violating I3
(History Immutability). Compensation (adding a new corrective state transition)
is the sanctioned approach, defined in Cycle 3.
