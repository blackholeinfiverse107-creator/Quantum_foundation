# Cycle 2 — Measurement Semantics Specification
# Deterministic Measurement & Collapse Framework
# Date: 2026-03-02  |  Author: Kanishk Singh

---

## 1. Purpose

The Measurement & Collapse Framework (MCF) provides the foundational primitive
for extracting classical information from a quantum-aligned state. It sits above
Cycle 1's Sovereign State Evolution Engine and consumes `StateVector` instances
to produce `MeasurementResult` objects.

The MCF enforces that:
- Every measurement **costs** information (declared, not hidden)
- Collapse is **irreversible** and permanently logged
- No measurement is possible without an explicit, single-use `CollapseToken`
- The same measurement (same state + same seed) always produces the same result

---

## 2. Measurement Cost (Quantum Alignment)

### 2.1 Why Measurement Must Destroy Information

In quantum mechanics, measurement projects the state onto one of the basis
eigenstates. Before measurement, the system exists in superposition — all basis
states have non-zero probability amplitude. After projective measurement:

- One amplitude becomes 1 (the observed eigenstate)
- All others become 0 (the un-observed states)

The pre-measurement superposition contains classical Shannon entropy:

```
H(pre) = -∑ p_i log₂(p_i)   where p_i = |α_i|²
```

The post-measurement state has H(post) = 0 (pure eigenstate). Therefore:

```
Information Loss = H(pre) - H(post) = H(pre) ≥ 0
```

This loss is not recoverable. This framework declares it explicitly.

### 2.2 Information Loss ≠ Error

Information loss is not a defect — it is a fundamental property of measurement.
Hiding it (returning a measurement result without declaring the loss) would be
architecturally dangerous, as downstream systems would make decisions assuming
more information persists than actually does.

---

## 3. Measurement Policies

### 3.1 ProjectiveMeasurementPolicy

Full von Neumann collapse. The state is fully projected onto one basis eigenstate.

| Property | Value |
|---|---|
| Post-state | Pure eigenstate (\|outcome⟩) |
| Information loss | = H(pre) (full entropy) |
| Repeat measurement | Idempotent — same outcome always |
| Reversibility | NONE |

### 3.2 WeakMeasurementPolicy(α)

Partial collapse parameterized by coupling strength α ∈ (0, 1].

| Property | Value |
|---|---|
| α = 1.0 | Equivalent to projective |
| α → 0.0 | Approaching identity (no collapse) |
| Post-state | Partial eigenstate (boosted/suppressed) |
| Information loss | ≈ α × H(pre) |
| Reversibility | NONE (all collapses are irreversible) |

---

## 4. Collapse Engine

### 4.1 Token Gating

Every collapse requires a `CollapseToken`. Tokens are:
- Single-use (consuming a token makes it permanently invalid)
- Issued by the CollapseEngine for registered policies only
- Not re-issuable with the same token_id after consumption

This models that measurement is a deliberate, authorized act — not a side effect.

### 4.2 Deterministic Seeds

The `collapse()` method requires an explicit integer seed. The seed is fed
into a SHA-256-based deterministic sampler. There is NO hidden RNG state.
Given the same pre-collapse state and seed, the outcome is ALWAYS identical.

### 4.3 Irreversible Collapse Events

Every `collapse()` call produces an `IrreversibleCollapseEvent`:
- Frozen (immutable dataclass)
- Stored in an append-only log
- Contains: pre-state, result, token_id, timestamp

The events constitute a complete audit trail of all information destruction.

---

## 5. Collapse Guarantees

| ID | Guarantee |
|---|---|
| M1 | Probability normalization: Born-rule probabilities sum to 1 |
| M2 | Declared information loss ≥ 0 |
| M3 | Collapse log event IDs strictly increasing |
| M4 | Repeat measurement idempotent for post-collapse states |
| M5 | Deterministic replay: same seed → same outcome |
| M6 | Confidence ∈ [0, 1] |
| M7 | Post-collapse state is a valid unit StateVector |

---

## 6. Failure Boundary Definitions

| Failure Mode | Handling |
|---|---|
| Token reuse | ValueError raised before collapse begins |
| Unregistered policy token | ValueError |
| Non-token passed to collapse() | TypeError |
| Policy re-registration | ValueError |
| Post-collapse norm violation | Caught by StateVector constructor (raises) |
| Zero-probability outcome selected | Handled by _seeded_sample fallback |
| Coupling strength = 0 | Rejected at WeakMeasurementPolicy.__init__ |

---

## 7. Non-Guarantees

1. The MCF does NOT guarantee which outcome will be selected for a given state.
   Only that the same seed always selects the same outcome.
2. The MCF does NOT integrate with Cycle 1 state evolution automatically.
   The caller is responsible for bridging the post-collapse state back into
   the evolution engine if desired.
3. The MCF does NOT perform multiple-observable simultaneous measurement
   (commuting observables). That is a higher-level concern.
