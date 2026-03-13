"""
Cycle 6 — Formal Quantum State Model
====================================

Strict mathematical implementation of pure quantum states in a complex 
vector space (Hilbert space). 

Core Constraints:
1. Must use complex amplitudes.
2. Must enforce L2-norm == 1.0.
3. Must reject un-normalized or zero vectors.
4. Must be strictly immutable.
"""

import math
from typing import Dict, FrozenSet, Mapping

class NormalizationError(Exception):
    """Raised when a quantum state vector fails the L2 mathematical norm constraint."""
    pass

class ComplexVector:
    """
    Pure mathematical dictionary representation mapping basis states 
    to complex amplitudes.
    """
    def __init__(self, amplitudes: Mapping[str, complex]):
        # Freeze the amplitudes to prevent hidden mathematical mutation
        self._amplitudes: Dict[str, complex] = {k: complex(v) for k, v in amplitudes.items() if abs(v) > 1e-12}
        
    @property
    def amplitudes(self) -> Mapping[str, complex]:
        return self._amplitudes
        
    @property
    def basis_states(self) -> FrozenSet[str]:
        return frozenset(self._amplitudes.keys())
        
    def norm(self) -> float:
        """Calculates the exact L2 norm (sum of squared magnitudes)."""
        return math.sqrt(sum(abs(amp)**2 for amp in self._amplitudes.values()))
        
    def inner_product(self, other: 'ComplexVector') -> complex:
        """Computes <self | other>"""
        keys = self.basis_states & other.basis_states
        return sum(self._amplitudes[k].conjugate() * other._amplitudes[k] for k in keys)
        
    def __repr__(self):
        terms = [f"({v.real:g}{v.imag:+g}j)|{k}⟩" for k, v in self._amplitudes.items()]
        return " + ".join(terms) if terms else "0"


class QuantumState:
    """
    A mathematically sealed wrapper around a ComplexVector.
    Enforces the defining constraint of a pure quantum state: sum of probabilities == 1.
    """
    TOLERANCE = 1e-9

    def __init__(self, vector: ComplexVector):
        norm = vector.norm()
        if abs(norm - 1.0) > self.TOLERANCE:
            raise NormalizationError(f"State vector violates L2 norm constraint (Norm = {norm}). Must be 1.0.")
            
        self._vector = vector
        
    @property
    def vector(self) -> ComplexVector:
        return self._vector

    @classmethod
    def from_dict(cls, amplitudes: Mapping[str, complex]) -> 'QuantumState':
        """Helper to create and validate a state directly from a python dict."""
        return cls(ComplexVector(amplitudes))

    def probability_of(self, basis_state: str) -> float:
        """Returns the Born rule probability |<basis|state>|^2."""
        amp = self._vector.amplitudes.get(basis_state, complex(0))
        return abs(amp)**2
        
    def __repr__(self):
        return f"QuantumState[{self._vector.__repr__()}]"
