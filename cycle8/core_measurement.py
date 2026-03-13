"""
Cycle 8 — Core Measurement Determinism Harness
==============================================

Mathematical seal for quantum collapse over a defined Hilbert space.

Enforcements:
1. Exact probability projection (Born rule via <psi|P|psi>).
2. Probabilities must sum EXACTLY to 1.0 (Information conservation before collapse).
3. Irreversible post-measurement renormalization.
4. Determinism via explicit Random seeding.
"""

import math
import random
from typing import Mapping, Tuple

from cycle8.core_state import QuantumState, InvariantViolation
from cycle8.core_operators import LinearOperator


class IncompletePOVMError(InvariantViolation):
    """Raised if measurement probabilities do not sum to 1.0 across the basis."""
    pass


class ProjectionOperator(LinearOperator):
    """
    A mathematical projection operator P, where P^dagger = P and P^2 = P.
    """
    TOLERANCE = 1e-9

    def __init__(self, matrix: Mapping[Tuple[str, str], complex]):
        super().__init__(matrix)
        self._verify_hermitian()

    def _verify_hermitian(self):
        """P^dagger must equal P"""
        dag = self.dagger()._matrix
        for k, v in self._matrix.items():
            dag_val = dag.get(k, complex(0))
            if abs(v - dag_val) > self.TOLERANCE:
                raise InvariantViolation("Measurement Projector must strictly be Hermitian.")

    def expectation(self, state: QuantumState) -> float:
        """Calculates <psi | P | psi> deterministically."""
        p_vec = self.apply(state.vector)
        # Inner product from cycle7: <bra | ket>
        inner_val = state.vector.inner(p_vec)
        # Structural boundary: projection expectation must be purely real
        if abs(inner_val.imag) > self.TOLERANCE:
            raise InvariantViolation("Expectation value of a Hermitian operator must be strictly real.")
        return inner_val.real


class MeasurementHarness:
    """
    Sealed, deterministic measurement mathematical layer.
    """
    
    @staticmethod
    def collapse(
        state: QuantumState, 
        projectors: Mapping[str, ProjectionOperator], 
        seed: int
    ) -> Tuple[str, QuantumState]:
        """
        1. Verifies probability sum = 1.0.
        2. deterministically samples outcome.
        3. Returns strictly normalized collapsed state.
        """
        probabilities = {}
        total_p = 0.0
        
        for name, P in projectors.items():
            p = P.expectation(state)
            if p > 0.0:
                probabilities[name] = p
                total_p += p
                
        # Invariant: Complete basis measurement must sum to 1.0
        if abs(total_p - 1.0) > 1e-6:
            raise IncompletePOVMError(f"Measurement error: Probabilities sum to {total_p}. The set of Projection Operators is incomplete.")

        # Deterministic seeded collapse
        rng = random.Random(seed)
        roll = rng.random()
        
        cumulative = 0.0
        selected = None
        for name, p in probabilities.items():
            cumulative += p
            if roll <= cumulative:
                selected = name
                break
                
        # Fallback to last valid branch on floating point edge issues
        if not selected:
            selected = list(probabilities.keys())[-1]
            
        p_selected = probabilities[selected]
        P_selected = projectors[selected]
        
        # Mathematical Projection
        collapsed_vec = P_selected.apply(state.vector)
        
        # Post-measurement Normalization: |psi'> = P|psi> / sqrt(p)
        renorm_factor = 1.0 / math.sqrt(p_selected)
        normalized_vec = collapsed_vec * renorm_factor
        
        # Re-wrap and explicitly trigger Norm=1 invariant check
        final_state = QuantumState(normalized_vec)
        
        return selected, final_state
