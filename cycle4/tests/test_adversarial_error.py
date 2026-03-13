"""
Cycle 4 Tests — Adversarial Error Validation
============================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle1.state_evolution_engine import StateVector, SovereignStateEngine, Observation, identity_rule, phase_rotation_rule
from cycle2.measurement_policy import ProjectiveMeasurementPolicy
from cycle2.collapse_engine import CollapseEngine
from cycle3.timeline import CausalTimeline, CausalityViolationError
from cycle4.error_model import ErrorModel, UnitaryNoise
from cycle4.correction_primitives import CorrectionEngine, SyndromeToken
from cycle4.error_enforcement_engine import ErrorEnforcementEngine
from cycle4.invariants import run_all_error_invariants, InvariantViolationError, check_no_free_restoration


def _uniform_2d() -> StateVector:
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


class TestErrorInvariants(unittest.TestCase):

    def setUp(self):
        self.initial_state = _uniform_2d()
        self.state_engine = SovereignStateEngine(self.initial_state)
        self.state_engine.register_rule("identity", identity_rule)
        
        self.collapse_engine = CollapseEngine()
        self.collapse_engine.register_policy(ProjectiveMeasurementPolicy())
        
        self.timeline = CausalTimeline()
        self.engine = ErrorEnforcementEngine(self.initial_state, self.state_engine, self.collapse_engine, self.timeline)

    def test_e1_unrecoverable_bounds(self):
        """E1: Measurement disturbance cannot be erased."""
        tok = self.collapse_engine.issue_token("ProjectiveMeasurement", "tok1")
        self.engine.measure_with_disturbance(tok, seed=42)
        
        # Total info loss in collapse engine must be <= tracked loss in error model
        res = self.engine.run_error_invariants()
        self.assertIn("E1_UNRECOVERABLE_BOUNDS", res.passed)
        
        # Adversarial tamper: artificially lower logged error
        self.engine.error_model._total_info_loss = -0.1
        res_fail = self.engine.run_error_invariants()
        self.assertIn("E1_UNRECOVERABLE_BOUNDS", res_fail.failed[0])

    def test_e2_no_free_restoration(self):
        """E2: Negative information loss declared in a collapse represents silent magic cooling (forbidden)."""
        # Directly mock a bad event
        import dataclasses
        class MockEvent:
            def __init__(self, id):
                self.causal_id = id
                self.event_type = "COLLAPSE"
                class Res:
                    information_loss_declared = -1.0 # Impossible free restoration
                self.payload = type('Payload', (), {'result': Res()})()
                
        with self.assertRaises(InvariantViolationError):
            check_no_free_restoration([MockEvent(1)])

    def test_e4_compensation_traceability(self):
        """E4: Correction events must be explicitly tagged as timeline compensations."""
        syn = SyndromeToken(detected_error="phase_flip", confidence=0.99)
        self.engine.apply_syndrome_correction(syn)
        res = self.engine.run_error_invariants()
        self.assertIn("E4_COMPENSATION_TRACEABILITY", res.passed)
        
        # Adversarial: Add a fake correction not tagged correctly
        ev = self.timeline.record("CORRECTION", {"fake": True})
        res2 = self.engine.run_error_invariants()
        self.assertNotIn("E4_COMPENSATION_TRACEABILITY", res2.passed)


class TestAdversarialError(unittest.TestCase):

    def setUp(self):
        self.initial_state = _uniform_2d()
        self.state_engine = SovereignStateEngine(self.initial_state)
        self.state_engine.register_rule("phase", phase_rotation_rule)
        self.collapse_engine = CollapseEngine()
        self.timeline = CausalTimeline()
        self.engine = ErrorEnforcementEngine(self.initial_state, self.state_engine, self.collapse_engine, self.timeline)

    def test_silent_state_reset_rejected(self):
        """Prove that physical state degrades and cannot silently restore without SyndromeToken."""
        obs = Observation("phase", (math.pi/2,))
        noisy_state, _ = self.engine.evolve_with_noise(obs, noise_fidelity=0.8)
        
        # The fidelity dropped. We cannot just assign physical_state = ideal_state.
        self.assertNotEqual(noisy_state, self.engine._ideal_state)
        
        # To correct it, we MUST use apply_syndrome_correction.
        # If we just mutate it internally (impossible via API as StateVector is frozen), we violate history.
        syn = SyndromeToken("phase_drift", 0.9)
        self.engine.apply_syndrome_correction(syn)
        self.assertEqual(self.engine.physical_state, self.engine._ideal_state)


if __name__ == "__main__":
    unittest.main(verbosity=2)
