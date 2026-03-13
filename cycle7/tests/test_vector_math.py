"""
Cycle 7 Tests — Validation of Pure Complex Vector Space Axions
==============================================================

Proves that the mathematical foundation strictly obeys all 
Hilbert space requirements without importing any quantum architecture.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
import math
from cycle7.complex_vector import ComplexVector, NonComplexValueError


class TestComplexVectorInstantiations(unittest.TestCase):
    
    def test_strict_complex_typing(self):
        """Enforces that only numeric mapping to complex is allowed."""
        valid_vec = ComplexVector({"x": 1+2j, "y": 0.5})
        self.assertEqual(valid_vec.amplitudes["y"], 0.5+0j)
        
        with self.assertRaises(NonComplexValueError):
             # String data rejected as amplitude
             ComplexVector({"x": "not-a-number"})

    def test_zero_pruning(self):
        """Proof: Exactly zero amplitudes are structurally dropped to save sparse space."""
        vec = ComplexVector({"x": 1.0, "y": 0.0, "z": 0.0j})
        self.assertIn("x", vec.basis_states)
        self.assertNotIn("y", vec.basis_states)
        self.assertNotIn("z", vec.basis_states)

    def test_immutability(self):
        """Proof: Internal amplitudes mapping cannot be externally modified."""
        vec = ComplexVector({"x": 1.0})
        # Try to hack the property
        with self.assertRaises(TypeError):
            vec.amplitudes["x"] = 2.0


class TestVectorMathematics(unittest.TestCase):

    def setUp(self):
        self.u = ComplexVector({"a": 1.0+0j, "b": 0.0+1j})
        self.v = ComplexVector({"a": 2.0+0j, "b": -1.0+0j})
        self.w = ComplexVector({"b": 1.0+0j, "c": 3.0+0j})

    def test_addition_commutativity(self):
        """Axiom: u + v == v + u"""
        r1 = self.u + self.v
        r2 = self.v + self.u
        self.assertEqual(r1, r2)
        
    def test_addition_associativity(self):
        """Axiom: (u + v) + w == u + (v + w)"""
        r1 = (self.u + self.v) + self.w
        r2 = self.u + (self.v + self.w)
        self.assertEqual(r1, r2)
        
    def test_scalar_multiplication(self):
        """Axiom: Distributivity a(u + v) == au + av"""
        alpha = 2.0 + 1j
        r1 = (self.u + self.v) * alpha
        r2 = (self.u * alpha) + (self.v * alpha)
        
        # We test explicit floating equality using norm of difference == 0
        diff = r1 - r2
        self.assertAlmostEqual(diff.norm(), 0.0)


class TestInnerProductAxioms(unittest.TestCase):
    
    def setUp(self):
        self.u = ComplexVector({"x": 1.0+2j, "y": 3j})
        self.v = ComplexVector({"x": -2.0, "y": 1.0-1j})
        self.w = ComplexVector({"x": 0.5, "z": 4.0})

    def test_conjugate_symmetry(self):
        """Axiom: <u|v> == <v|u>^*"""
        uv = self.u.inner(self.v)
        vu = self.v.inner(self.u)
        self.assertAlmostEqual(uv, vu.conjugate())

    def test_linearity_in_ket(self):
        """Axiom: <u | a*v + b*w> == a<u|v> + b<u|w>"""
        alpha = 2.0
        beta = -1.0 + 1j
        
        ket = (self.v * alpha) + (self.w * beta)
        result1 = self.u.inner(ket)
        
        result2 = (self.u.inner(self.v) * alpha) + (self.u.inner(self.w) * beta)
        
        self.assertAlmostEqual(result1, result2)
        
    def test_antilinearity_in_bra(self):
        """Axiom: <a*u | v> == a^* <u|v>"""
        alpha = 1.0 + 2j
        bra_vec = self.u * alpha
        
        result1 = bra_vec.inner(self.v)
        result2 = alpha.conjugate() * self.u.inner(self.v)
        
        self.assertAlmostEqual(result1, result2)

    def test_positive_definiteness(self):
        """Axiom: <v|v> >= 0, and == 0 iff v == 0"""
        inner_uu = self.u.inner(self.u)
        
        self.assertAlmostEqual(inner_uu.imag, 0.0) # Strictly real
        self.assertGreater(inner_uu.real, 0.0)     # Strictly positive
        
        zero_vec = ComplexVector({})
        self.assertAlmostEqual(zero_vec.inner(zero_vec), 0.0)

    def test_norm_derivation(self):
        """Proof: Norm is explicitly sqrt(<v|v>)."""
        inner_uu = self.u.inner(self.u)
        self.assertAlmostEqual(self.u.norm(), math.sqrt(inner_uu.real))

    def test_triangle_inequality(self):
        """Axiom: ||u + v|| <= ||u|| + ||v||"""
        n_sum = (self.u + self.v).norm()
        n_sep = self.u.norm() + self.v.norm()
        self.assertLessEqual(n_sum, n_sep + 1e-9)


if __name__ == "__main__":
    unittest.main(verbosity=2)
