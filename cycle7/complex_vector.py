"""
Cycle 7 — Pure Complex Vector Space
===================================

A standalone, zero-dependency mathematical foundation for an arbitrary-dimensional
vector space over the complex field $\\mathbb{C}$.

Mathematical Axioms Enforced:
1. Addition is commutative and associative.
2. Scalar multiplication distributes over addition.
3. Inner product is conjugate symmetric: $\\langle u | v \\rangle = \\langle v | u \\rangle^*$.
4. Inner product is linear in the second argument, antilinear in the first.
5. Norm is positive definite: $\\|v\\| \\ge 0$, and $\\|v\\| = 0 \\iff v = 0$.

Design Constraints:
- Immutable (no hidden state mutations).
- Rejects non-complex values strictly.
- Dimensionless string mapping to support sparse infinite spaces.
"""

import math
from typing import Mapping, FrozenSet, Union


class NonComplexValueError(TypeError):
    """Raised when a mathematically non-complex (or non-coercible) scalar is used."""
    pass


class ComplexVector:
    """
    Immutable representation of a mathematical vector in a complex Hilbert space.
    """
    __slots__ = ('_amplitudes',)

    def __init__(self, amplitudes: Mapping[str, Union[complex, float, int]]):
        cleaned = {}
        for k, v in amplitudes.items():
            if not isinstance(v, (complex, float, int)):
                raise NonComplexValueError(f"Scalar amplitude for basis '{k}' must be complex/numeric, got {type(v)}.")
            
            # Coerce to strict complex type and prune true zeros
            c_val = complex(v)
            if abs(c_val) > 0.0:
                cleaned[k] = c_val

        self._amplitudes: Mapping[str, complex] = cleaned

    @property
    def amplitudes(self) -> Mapping[str, complex]:
        import types
        return types.MappingProxyType(self._amplitudes)

    @property
    def basis_states(self) -> FrozenSet[str]:
        return frozenset(self._amplitudes.keys())
        
    def __eq__(self, other: object) -> bool:
        """Mathematical equality of vectors."""
        if not isinstance(other, ComplexVector):
            return False
            
        all_keys = self.basis_states | other.basis_states
        for k in all_keys:
            v1 = self._amplitudes.get(k, complex(0))
            v2 = other._amplitudes.get(k, complex(0))
            
            # Strict floating point equality for exact mathematical zero vs zero
            # In practical uses we might need tolerance, but to prove axioms we stay strict
            if abs(v1 - v2) > 1e-12:
                return False
        return True

    def __add__(self, other: 'ComplexVector') -> 'ComplexVector':
        """Vector addition: |u> + |v>"""
        if not isinstance(other, ComplexVector):
            return NotImplemented
            
        new_amps = dict(self._amplitudes)
        for k, v in other.amplitudes.items():
            new_amps[k] = new_amps.get(k, complex(0)) + v
            
        return ComplexVector(new_amps)

    def __sub__(self, other: 'ComplexVector') -> 'ComplexVector':
        """Vector subtraction: |u> - |v>"""
        if not isinstance(other, ComplexVector):
            return NotImplemented
        return self.__add__(other * -1.0)

    def __mul__(self, scalar: Union[complex, float, int]) -> 'ComplexVector':
        """Scalar multiplication from the right: |v> * alpha"""
        if not isinstance(scalar, (complex, float, int)):
            raise NonComplexValueError(f"Must multiply by a complex/numeric scalar, got {type(scalar)}.")
            
        c_scalar = complex(scalar)
        
        # Zero scalar maps everything to the zero vector natively
        if abs(c_scalar) == 0.0:
            return ComplexVector({})
            
        return ComplexVector({k: v * c_scalar for k, v in self._amplitudes.items()})

    def __rmul__(self, scalar: Union[complex, float, int]) -> 'ComplexVector':
        """Scalar multiplication from the left: alpha * |v>"""
        return self.__mul__(scalar)

    def inner(self, other: 'ComplexVector') -> complex:
        """
        Inner product: <self | other>
        Mathematical property: self is the "bra" (conjugated), other is the "ket".
        """
        if not isinstance(other, ComplexVector):
            raise TypeError("Inner product requires another ComplexVector.")
            
        common_bases = self.basis_states & other.basis_states
        return sum(self._amplitudes[k].conjugate() * other.amplitudes[k] for k in common_bases)

    def norm(self) -> float:
        """
        L2-norm derived strictly from the inner product: ||v|| = sqrt(<v|v>).
        Math constraint: Must be >= 0.
        """
        inner_self = self.inner(self)
        
        # <v|v> is strictly real and positive definite. Strip tiny imaginary drift if any.
        assert abs(inner_self.imag) < 1e-12, "Mathematical violation: inner product of self with self must be strictly real."
        
        return math.sqrt(inner_self.real)

    def normalized(self) -> 'ComplexVector':
        """Returns a new vector in the same direction but with norm=1.0"""
        n = self.norm()
        if n == 0.0:
            raise ValueError("The zero vector cannot be normalized.")
        return self * (1.0 / n)

    def is_zero(self) -> bool:
        """Checks if this is the zero vector (|v| == 0)."""
        return len(self._amplitudes) == 0

    def __repr__(self) -> str:
        if self.is_zero():
            return "0"
        terms = [f"({v.real:g}{v.imag:+g}j)|{k}⟩" for k, v in self._amplitudes.items()]
        return " + ".join(terms)
