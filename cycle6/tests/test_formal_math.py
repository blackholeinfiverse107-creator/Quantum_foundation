"""
Cycle 6 Tests — Formal Mathematical Validations
===============================================

Proves that the Hilbert space representation strictly enforces:
1. Normalization bounds on raw states.
2. Unitarity on evolution operators.
3. Orthogonal projection properties during measurement.
4. Correct Born-rule collapse and re-normalization.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle6.formal_state import ComplexVector, QuantumState, NormalizationError
from cycle6.operators import (
    LinearOperator, 
    UnitaryOperator, 
    NonUnitaryError,
    build_pauli_x,
    build_hadamard
)
from cycle6.measurement_math import (
    ProjectionOperator, 
    MeasurementMath,
    build_z_basis_projectors
)


class TestFormalQuantumState(unittest.TestCase):
    def test_normalization_enforcement(self):
        """Proof: Cannot instantiate a QuantumState with L2-norm != 1"""
        
        # Valid state 1/sqrt(2) |0> + 1/sqrt(2) |1>
        amp = 1.0 / math.sqrt(2)
        valid_vec = ComplexVector({"0": complex(amp), "1": complex(amp)})
        state = QuantumState(valid_vec)
        self.assertAlmostEqual(state.vector.norm(), 1.0)
        
        # Invalid state: |0> + |1> (norm = sqrt(2), not 1)
        invalid_vec = ComplexVector({"0": complex(1.0), "1": complex(1.0)})
        with self.assertRaises(NormalizationError):
            QuantumState(invalid_vec)
            
    def test_probability_calculation(self):
        """Proof: Probability strictly matches Born rule for basis states."""
        amp = 1.0 / math.sqrt(2)
        state = QuantumState(ComplexVector({"0": complex(amp), "1": complex(amp)}))
        
        self.assertAlmostEqual(state.probability_of("0"), 0.5)
        self.assertAlmostEqual(state.probability_of("1"), 0.5)
        self.assertEqual(state.probability_of("2"), 0.0)


class TestOperatorMathematics(unittest.TestCase):
    def test_unitarity_enforcement(self):
        """Proof: UnitaryOperator enforces U^dagger U = I."""
        
        # A valid unitary: Pauli-X
        basis = {"0", "1"}
        x_gate = build_pauli_x(basis)
        self.assertIsInstance(x_gate, UnitaryOperator)
        
        # An invalid matrix: e.g. non-orthogonal columns
        bad_matrix = {
            ("0", "0"): complex(1.0),
            ("1", "0"): complex(0.0),
            ("0", "1"): complex(1.0), # Duplicate column vector
            ("1", "1"): complex(0.0)
        }
        with self.assertRaises(NonUnitaryError):
            UnitaryOperator(bad_matrix)

    def test_hadamard_evolution(self):
        """Proof: Hadamard creates superposition deterministically."""
        basis = {"0", "1"}
        h_gate = build_hadamard(basis)
        
        # Start in |0>
        initial = QuantumState(ComplexVector({"0": complex(1.0)}))
        
        # Evolve
        final = h_gate.evolve(initial)
        
        # Must be 1/sqrt(2) |0> + 1/sqrt(2) |1>
        amp = 1.0 / math.sqrt(2)
        self.assertAlmostEqual(final.probability_of("0"), 0.5)
        self.assertAlmostEqual(final.probability_of("1"), 0.5)
        
        # Evolve again H * H = I
        identity_state = h_gate.evolve(final)
        self.assertAlmostEqual(identity_state.probability_of("0"), 1.0)


class TestMeasurementCollapseMath(unittest.TestCase):
    def test_projective_measurement(self):
        """Proof: Measurement mathematically projects the state and renormalizes."""
        basis = {"0", "1"}
        projectors = build_z_basis_projectors(basis)
        
        # Test 1: Measure a pure superposition state
        amp = 1.0 / math.sqrt(2)
        superposition = QuantumState(ComplexVector({"0": complex(amp), "1": complex(amp)}))
        
        # Deterministically collapse with seed
        outcome, collapsed_state = MeasurementMath.projective_measurement(superposition, projectors, seed=42)
        
        # The new state MUST be re-normalized to 1.0 probability on the outcome.
        self.assertAlmostEqual(collapsed_state.probability_of(outcome), 1.0)
        
        # Ensure it creates a valid QuantumState (L2-norm = 1 internally verified)
        self.assertIsInstance(collapsed_state, QuantumState)

    def test_idempotence(self):
        """Proof: Repeated measurement of the same basis yields the exact same state."""
        basis = {"0", "1"}
        projectors = build_z_basis_projectors(basis)
        
        amp = 1.0 / math.sqrt(2)
        superposition = QuantumState(ComplexVector({"0": complex(amp), "1": complex(amp)}))
        
        # First measurement
        out1, state1 = MeasurementMath.projective_measurement(superposition, projectors, seed=12)
        
        # Second measurement (even with different seed, probability is 1.0 for out1)
        out2, state2 = MeasurementMath.projective_measurement(state1, projectors, seed=99)
        
        self.assertEqual(out1, out2)
        self.assertEqual(state1.probability_of(out1), 1.0)
        self.assertEqual(state2.probability_of(out2), 1.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
