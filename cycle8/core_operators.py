"""
Cycle 8 — Core Operator Mathematical Seal
=========================================

Calculus for strictly constrained Hilbert space operations.

Enforcements:
1. Linear mapping over cycle7.ComplexVector.
2. Unitary invariant check: U^dagger * U = I.
3. Dimension tracking (for explicit boundary sealing).
"""

from typing import Mapping, Tuple

from cycle7.complex_vector import ComplexVector
from cycle8.core_state import QuantumState, InvariantViolation


class NonUnitaryInvariantError(InvariantViolation):
    """Raised when an operator mathematically fails the U^dagger U = I check."""
    pass


class LinearOperator:
    """
    A purely linear transformation matrix on a ComplexVector space.
    """
    def __init__(self, matrix: Mapping[Tuple[str, str], complex]):
        self._matrix = {k: complex(v) for k, v in matrix.items() if abs(v) > 1e-12}

    def apply(self, vector: ComplexVector) -> ComplexVector:
        """Applies the linear map to a vector, returning a new mathematical vector."""
        if not isinstance(vector, ComplexVector):
            raise TypeError("Operator expects a ComplexVector.")
            
        new_amplitudes = {}
        for (row, col), matrix_amp in self._matrix.items():
            vec_amp = vector.amplitudes.get(col, complex(0))
            if abs(vec_amp) > 0.0:
                new_amplitudes[row] = new_amplitudes.get(row, complex(0)) + matrix_amp * vec_amp
                
        return ComplexVector(new_amplitudes)

    def dagger(self) -> 'LinearOperator':
        """Conjugate transpose required for Unitary checks and Observables."""
        dag = {(col, row): amp.conjugate() for (row, col), amp in self._matrix.items()}
        return LinearOperator(dag)

    def __mul__(self, other: 'LinearOperator') -> 'LinearOperator':
        """Matrix multiplication: Self * Other"""
        new_matrix = {}
        # Naive matrix multiply for sparse structures
        # To compute C = A * B, C_{ik} = \sum_j A_{ij} B_{jk}
        for (rA, cA), vA in self._matrix.items():
            for (rB, cB), vB in other._matrix.items():
                if cA == rB: # Matching inner dimension
                    new_matrix[(rA, cB)] = new_matrix.get((rA, cB), complex(0)) + vA * vB
        return LinearOperator(new_matrix)


class UnitaryOperator(LinearOperator):
    """
    A foundational sealed operator representing a valid quantum logic gate or evolution.
    """
    TOLERANCE = 1e-9

    def __init__(self, matrix: Mapping[Tuple[str, str], complex]):
        super().__init__(matrix)
        self._seal_unitarity_invariant()

    def _seal_unitarity_invariant(self):
        """
        Mathematically guarantees that U^dagger U = I.
        This represents the reversibility and conservation of total probability.
        """
        # We explicitly calculate U^dagger * U
        dag = self.dagger()
        identity_test = dag * self
        
        # Determine the effective subspace (all columns must map to columns)
        effective_basis = {col for (row, col) in self._matrix.keys()}
        
        # Verify that identity_test is the Identity matrix on the effective subspace
        for row, col in identity_test._matrix.keys():
            val = identity_test._matrix[(row, col)]
            if row == col:
                if abs(val - 1.0) > self.TOLERANCE:
                    raise NonUnitaryInvariantError(f"Unitarity failed: Diagonal element ({row},{col}) norm is {abs(val)}, expected 1.0")
            else:
                if abs(val) > self.TOLERANCE:
                    raise NonUnitaryInvariantError(f"Unitarity failed: Off-diagonal element ({row},{col}) is {val}, expected 0.0")
                    
        # Verify coverage
        for basis in effective_basis:
            if abs(identity_test._matrix.get((basis, basis), 0.0) - 1.0) > self.TOLERANCE:
                 raise NonUnitaryInvariantError(f"Unitarity failed: Missing norm conservation on basis {basis}")

    def evolve(self, state: QuantumState) -> QuantumState:
        """
        Deterministic, sealed state evolution.
        Because U is Unitary and State is Normalized, the output vector MUST be normalized.
        We pass it to QuantumState, which explicitly verifies the Norm=1 invariant anyway.
        """
        new_vec = self.apply(state.vector)
        return QuantumState(new_vec)
