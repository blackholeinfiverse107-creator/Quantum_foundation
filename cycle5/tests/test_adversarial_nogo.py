"""
Cycle 5 Tests — Adversarial No-Go Boundary Validation
=====================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import copy
import unittest

from cycle1.state_evolution_engine import StateVector, SovereignStateEngine, Observation, identity_rule, phase_rotation_rule
from cycle2.measurement_policy import ProjectiveMeasurementPolicy, MeasurementResult
from cycle2.collapse_engine import CollapseEngine
from cycle3.timeline import CausalTimeline, CausalEvent
from cycle4.error_model import ErrorModel
from cycle5.nogo_primitives import (
    NoCloningViolation,
    NoDeletingViolation,
    ConfidenceCollapseViolation,
    StateReference
)
from cycle5.nogo_enforcement import NoGoEnforcementEngine
from cycle5.invariants import run_all_nogo_invariants


def _uniform_2d() -> StateVector:
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


class TestNoGoBoundaries(unittest.TestCase):

    def setUp(self):
        self.initial_state = _uniform_2d()
        self.state_engine = SovereignStateEngine(self.initial_state)
        self.state_engine.register_rule("identity", identity_rule)
        self.state_engine.register_rule("phase", phase_rotation_rule)
        
        self.collapse_engine = CollapseEngine()
        self.collapse_engine.register_policy(ProjectiveMeasurementPolicy())
        
        self.timeline = CausalTimeline()
        self.error_model = ErrorModel()
        self.engine = NoGoEnforcementEngine(self.state_engine, self.collapse_engine, self.timeline, self.error_model)
        self.ref = self.engine.root_reference

    def test_ng1_no_cloning(self):
        """NG1: A pure state reference cannot be duplicated (shallow or deep)."""
        # Python copy attempts
        with self.assertRaises(NoCloningViolation):
            _ = copy.copy(self.ref)
            
        with self.assertRaises(NoCloningViolation):
            _ = copy.deepcopy(self.ref)

        # Adversarial parallel evolution attempt (re-using old reference)
        obs1 = Observation("identity", ())
        _, _ = self.engine.evolve_strictly(self.ref, obs1)
        
        # Try to evolve a parallel branch using the same system bypassing linear timeline expected_id
        # In reality, expected_id advanced. Let's say an adversary reset the timeline:
        self.timeline._events.pop()
        
        # The engine should reject because the timeline length + 1 != expected_next
        with self.assertRaises(NoCloningViolation):
            self.engine.evolve_strictly(self.ref, obs1)

    def test_ng2_no_deleting(self):
        """NG2: State references and history cannot be silently erased."""
        # Try evolving a made-up un-registered reference
        fake_ref = StateReference("fake-1234")
        with self.assertRaises(NoDeletingViolation):
            self.engine.evolve_strictly(fake_ref, Observation("identity", ()))

        # Run invariants check on a tampered timeline
        self.timeline.record("STRICT_EVOLUTION", {})
        # Adversary manually removes an event
        self.timeline._events[0] = None
        
        res = run_all_nogo_invariants(self.timeline)
        self.assertTrue(any("NG2 Violation: Event index 0 is null" in f for f in res.failed))

    def test_ng3_confidence_collapse(self):
        """NG3: You cannot gain confidence without declaring information loss."""
        # We manually inject a violation object to prove the invariant catches it.
        class BadResult(MeasurementResult):
            def __init__(self):
                super().__init__("0", 0.99, 0.0, _uniform_2d(), 42, "FakePolicy") # 99% confidence, 0 info loss!
                
        bad_event = CausalEvent(1, "STRICT_COLLAPSE", type('Payload', (), {'result': BadResult()})(), None, 1000, False)
        self.timeline._events.append(bad_event)
        
        res = run_all_nogo_invariants(self.timeline)
        self.assertTrue(any("NG3_CONFIDENCE_COLLAPSE_BOUND" in f for f in res.failed))
        
    def test_integrated_pass(self):
        """A valid run passes all No-Go invariants."""
        obs = Observation("phase", (math.pi/2,))
        _, _ = self.engine.evolve_strictly(self.ref, obs)
        
        tok = self.collapse_engine.issue_token("ProjectiveMeasurement", "tok1")
        _, _, _ = self.engine.measure_strictly(self.ref, tok, seed=42)
        
        res = run_all_nogo_invariants(self.timeline)
        self.assertEqual(len(res.failed), 0)
        self.assertEqual(len(res.passed), 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
