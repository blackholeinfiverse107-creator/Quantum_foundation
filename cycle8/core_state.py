"""
Cycle 8 — Core State Enforcement Harness
========================================

Integrates the pure mathematical `ComplexVector` (from Cycle 7) into 
a structurally sealed `QuantumState`. 

Enforcements:
1. Zero abstraction leakage (ComplexVector is the only math state).
2. Norm = 1 invariant explicitly checked on every instantiation.
3. Rejection of implicit mutation (ComplexVector is immutable).
"""

from typing import Mapping, Union
from cycle7.complex_vector import ComplexVector, NonComplexValueError


class InvariantViolation(Exception):
    """Base class for any structural or mathematical invariant failure at the foundation layer."""
    pass


class NormalizationInvariantError(InvariantViolation):
    """Raised specifically when a state fails the L2-Norm = 1.0 boundary."""
    pass


class InvalidStateStructureError(InvariantViolation):
    """Raised when an empty or malformed vector is passed to State."""
    pass


class QuantumState:
    """
    A foundational wrapper forming the absolute mathematical base for quantum computation.
    
    Guarantees:
    - Inner state is ALWAYS a valid cycle7.ComplexVector.
    - Vector norm is ALWAYS 1.0 +/- 1e-9.
    """
    TOLERANCE = 1e-9

    def __init__(self, vector: ComplexVector):
        if not isinstance(vector, ComplexVector):
            raise InvalidStateStructureError("QuantumState must be initialized strictly with a cycle7.ComplexVector.")
            
        if vector.is_zero():
            raise InvalidStateStructureError("A quantum state cannot be the mathematical zero vector.")
            
        # Assert Norm = 1 Invariant
        n = vector.norm()
        if abs(n - 1.0) > self.TOLERANCE:
            raise NormalizationInvariantError(f"Hilbert space constraint violated: State vector L2-norm is {n}, exactly 1.0 required.")
            
        self._vector = vector

    @property
    def vector(self) -> ComplexVector:
        """Returns the immutable mathematical representation of the state."""
        return self._vector

    @classmethod
    def from_dict(cls, amplitudes: Mapping[str, Union[complex, float, int]]) -> 'QuantumState':
        """
        Integration harness initialization.
        Safe construction from pure dictionaries mapping basis states to scalars.
        """
        try:
            vec = ComplexVector(amplitudes)
            return cls(vec)
        except NonComplexValueError as e:
            raise InvalidStateStructureError(f"Mathematical type error in amplitudes: {e}")

    def probability_of(self, basis_state: str) -> float:
        """Calculates exact Born-rule probability: |<basis|psi>|^2"""
        amp = self._vector.amplitudes.get(basis_state, complex(0))
        return abs(amp)**2

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, QuantumState):
            return False
        return self._vector == other._vector

    def __repr__(self):
        return f"QuantumState[{self._vector.__repr__()}]"
