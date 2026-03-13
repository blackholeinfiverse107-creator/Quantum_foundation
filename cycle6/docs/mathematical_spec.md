# Cycle 6 — Formal Quantum State & Operator Spec
# Subsystem: Mathematical Computation Phase
# Date: 2026-03-02  |  Author: Kanishk Singh

---

## 1. Purpose

 Cycle 6 transitions from system-level architectural guardrails to internal 
 mathematical correctness. It dictates how the underlying physics engine must 
 represent quantum data computationally.

The framework strictly bounds state evolution using complex vector spaces, 
linear algebra, and physical constraints (unitarity, L2-norm preservation).

---

## 2. The Formal State Model (Hilbert Space)

A valid `QuantumState` relies entirely on a frozen `ComplexVector`.

**Constraints Enforced:**
1. **Linearity & Superposition:** The vector holds a dictionary of amplitudes mapping basis strings to complex floats.
2. **Probability Normalization:** The sum of squared magnitudes (`|amp|^2`) of all present basis states must equal `1.0` (within tolerance).
3. **No Hidden Mutation:** The complex amplitudes are structurally frozen on initialization. Evolving a state creates a new mapped state; the input state vector is never overwritten.

*Violations raise `NormalizationError` instantly.*

---

## 3. The Formal Operator Framework

Quantum operators represent physical actions, either extending logic (gates) 
or extracting data (measurements).

### 3.1 Unitary Evolution (Gates)
All standard quantum evolution MUST be unitary. A `UnitaryOperator` enforces 
that its adjoint equals its inverse ($U^\\dagger = U^{-1}$, meaning $U^\\dagger U = I$).

**Mathematical Consequence:**
Because $U^\\dagger U = I$, any unitary evolution preserves the inner product (and thus the L2-norm) of the initial state. Superposition is rotated perfectly without gaining or losing fundamental probabilities.
*Violations raise `NonUnitaryError` instantly.*

### 3.2 Projection Operators (Measurement)
Measurement represents interactions extracting classical info. They are modeled 
via `ProjectionOperator` matrices $P$.

**Mathematical Consequence:**
A projector is Hermitian ($P^\\dagger = P$) and idempotent ($P^2 = P$). 
Because $P^\\dagger P = P^2 = P \\neq I$, it intentionally fails Unitarity. 
Applying $P$ destroys orthogonal information in the superposition, causing 
deterministic loss of unobserved branches.

---

## 4. Measurement Math & Born Rule

The `MeasurementMath` module performs strict extraction, relying on probability projection mapping.

1. **Probability ($\langle \\psi | P | \\psi \\rangle$):** The probability of seeing outcome $k$ is perfectly proportional to the geometric inner product of the state and the projection matrix.
2. **Collapse ($P|\\psi\\rangle$):** The vector orthogonal to the result is discarded.
3. **Re-normalization:** The resulting vector is divided by $\\sqrt{p}$ to restore the L2-norm back to $1.0$.

---

## 5. Explicit Non-Guarantees

1. The mathematical framework proves truth **but does not execute hardware optimization.** Matrices are mapped logically in sparse dictionaries.
2. State dimensions are assumed validated at the interaction layer; the pure mathematical models apply linear algebra verbatim.

---

## 6. Handover Justification

The `cycle6.formal_state` package must form the **absolute lowest computational layer** used by the `cycle1.SovereignStateEngine`. Any external code claiming to evolve quantum states MUST use the `UnitaryOperator` interface. There is no other path.
