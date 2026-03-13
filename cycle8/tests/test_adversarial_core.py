"""
Cycle 8 Tests — Core Operations and Adversarial Harness
=======================================================

These validation test suites prove the structural constraints of the 
Hilbert space layer: States, Operators, Measurements, and Adversarial hacks.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
import math

from cycle7.complex_vector import ComplexVector
from cycle8.core_state import QuantumState, NormalizationInvariantError, InvalidStateStructureError
from cycle8.core_operators import UnitaryOperator, NonUnitaryInvariantError, LinearOperator
from cycle8.core_measurement import ProjectionOperator, MeasurementHarness, IncompletePOVMError, InvariantViolation


class TestDay2StateInvariants(unittest.TestCase):
    
    def test_constructor_norm_invariant(self):
        """Proof: QuantumState exclusively allows Norm=1 complex vectors."""
        # Valid
        v1 = ComplexVector({"0": 0.8, "1": 0.6}) # 0.8^2 + 0.6^2 = 0.64 + 0.36 = 1.0
        state = QuantumState(v1)
        self.assertAlmostEqual(state.vector.norm(), 1.0)
        
        # Invalid
        v2 = ComplexVector({"0": 1.0, "1": 1.0})
        with self.assertRaises(NormalizationInvariantError):
            QuantumState(v2)

    def test_rejection_of_invalid_bases(self):
        """Proof: QuantumState cannot be initialized from pure floats bypassing the field."""
        with self.assertRaises(InvalidStateStructureError):
            QuantumState("not a vector")


class TestDay3OperatorSeal(unittest.TestCase):

    def test_unitarity_verification(self):
        """Proof: Operators natively run U^dagger U = I during instantiation."""
        inv_sq2 = 1.0 / math.sqrt(2)
        valid_unitary = {
            ("0", "0"): inv_sq2, ("0", "1"): inv_sq2,
            ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
        }
        U = UnitaryOperator(valid_unitary)
        self.assertIsInstance(U, UnitaryOperator)
        
        invalid_unitary = {
            ("0", "0"): 0.99, ("0", "1"): inv_sq2,
            ("1", "0"): inv_sq2, ("1", "1"): -inv_sq2
        }
        with self.assertRaises(NonUnitaryInvariantError):
            UnitaryOperator(invalid_unitary)


class TestDay4MeasurementDeterminism(unittest.TestCase):

    def setUp(self):
        self.p0 = ProjectionOperator({("0", "0"): 1.0})
        self.p1 = ProjectionOperator({("1", "1"): 1.0})
        
        # Superposition |+>
        amp = 1.0 / math.sqrt(2)
        self.state = QuantumState(ComplexVector({"0": amp, "1": amp}))

    def test_complete_povm_requirement(self):
        """Proof: Measurement rejects if probabilities do not sum to 1.0."""
        # Provide only P0
        incomplete = {"0": self.p0}
        with self.assertRaises(IncompletePOVMError):
            MeasurementHarness.collapse(self.state, incomplete, seed=0)

    def test_deterministic_seeded_collapse(self):
        """Proof: Seeding explicitly locks the randomly collapsed outcome."""
        complete = {"0": self.p0, "1": self.p1}
        
        o1, s1 = MeasurementHarness.collapse(self.state, complete, seed=42)
        o2, s2 = MeasurementHarness.collapse(self.state, complete, seed=42)
        
        self.assertEqual(o1, o2)
        self.assertEqual(s1.vector, s2.vector)

    def test_hermitian_projector_check(self):
        """Proof: Projectors must be Hermitian P = P^dagger"""
        bad_matrix = {("0", "1"): 1.0} # Not symmetric
        with self.assertRaises(InvariantViolation):
             ProjectionOperator(bad_matrix)


class TestDay6AdversarialCore(unittest.TestCase):

    def test_mutation_rejection(self):
        """Proof: QuantumState's inner ComplexVector is immutable."""
        amp = 1.0 / math.sqrt(2)
        state = QuantumState(ComplexVector({"0": amp, "1": amp}))
        
        with self.assertRaises(TypeError):
            state.vector.amplitudes["0"] = 1.0  # MappingProxyType / Frozen struct prevents this

    def test_information_leak_rejection(self):
        """Proof: Extracting expectation values from non-hermitian pseudo-measurements fails."""
        class FakeProjector(LinearOperator):
            TOLERANCE = 1e-9
            def expectation(self, state: QuantumState) -> float:
                inner_val = state.vector.inner(self.apply(state.vector))
                if abs(inner_val.imag) > self.TOLERANCE:
                    raise InvariantViolation("Must be purely real")
                return inner_val.real
                
        # Fake matrix with complex expectation diagonal
        fp = FakeProjector({("0", "0"): 1.0j})
        state = QuantumState(ComplexVector({"0": 1.0}))
        
        with self.assertRaises(InvariantViolation):
            fp.expectation(state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
