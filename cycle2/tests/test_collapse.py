"""
Cycle 2 Tests — Collapse Determinism & Measurement Invariants
=============================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle1.state_evolution_engine import StateVector
from cycle2.measurement_policy import (
    ProjectiveMeasurementPolicy,
    WeakMeasurementPolicy,
    von_neumann_entropy,
    information_loss_after_collapse,
)
from cycle2.collapse_engine import CollapseEngine, CollapseToken
from cycle2.invariants import (
    run_all_measurement_invariants,
    check_repeat_measurement_idempotent,
    check_probability_normalization,
    MeasurementInvariantError,
)


def _uniform_2d() -> StateVector:
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


def _uniform_3d() -> StateVector:
    amp = 1.0 / math.sqrt(3)
    return StateVector({"0": complex(amp), "1": complex(amp), "2": complex(amp)})


class TestProjectiveMeasurementDeterminism(unittest.TestCase):

    def test_same_seed_same_outcome(self):
        """Same state + same seed → same outcome every time."""
        policy = ProjectiveMeasurementPolicy()
        state = _uniform_2d()
        results = [policy.measure(state, seed=42) for _ in range(20)]
        outcomes = {r.outcome for r in results}
        self.assertEqual(len(outcomes), 1, f"Got multiple outcomes: {outcomes}")

    def test_different_seeds_may_differ(self):
        """Different seeds can produce different outcomes (statistical property)."""
        policy = ProjectiveMeasurementPolicy()
        state = _uniform_2d()
        outcomes = {policy.measure(state, seed=i).outcome for i in range(100)}
        # For a fair coin (50/50), we expect both outcomes eventually
        self.assertGreater(len(outcomes), 1,
                           "All seeds produced the same outcome — seeding appears broken")

    def test_post_collapse_norm(self):
        """Post-collapse state must be a unit vector."""
        policy = ProjectiveMeasurementPolicy()
        result = policy.measure(_uniform_2d(), seed=42)
        check_probability_normalization(result.post_state)

    def test_post_collapse_is_eigenstate(self):
        """After projective measurement, one amplitude is 1 and all others are 0."""
        policy = ProjectiveMeasurementPolicy()
        result = policy.measure(_uniform_3d(), seed=42)
        post = result.post_state
        probs = [a.probability() for a in post.amplitudes]
        ones = [p for p in probs if abs(p - 1.0) < 1e-10]
        zeros = [p for p in probs if abs(p) < 1e-10]
        self.assertEqual(len(ones), 1)
        self.assertEqual(len(zeros), len(probs) - 1)

    def test_information_loss_is_declared(self):
        """Information loss must be >= 0 and < pre-measurement entropy."""
        policy = ProjectiveMeasurementPolicy()
        state = _uniform_2d()
        result = policy.measure(state, seed=42)
        pre_entropy = von_neumann_entropy(state)
        self.assertGreaterEqual(result.information_loss_declared, 0.0)
        self.assertLessEqual(result.information_loss_declared, pre_entropy + 1e-10)

    def test_repeat_measurement_idempotent(self):
        """Measuring post-collapse state multiple times must always return same outcome."""
        policy = ProjectiveMeasurementPolicy()
        result = policy.measure(_uniform_2d(), seed=42)
        check_repeat_measurement_idempotent(policy, result.post_state, seed=0)


class TestWeakMeasurement(unittest.TestCase):

    def test_weak_measurement_preserves_norm(self):
        """Post-weak-measurement state must still be unit vector."""
        policy = WeakMeasurementPolicy(coupling_strength=0.5)
        result = policy.measure(_uniform_2d(), seed=99)
        check_probability_normalization(result.post_state)

    def test_weak_measurement_less_information_loss(self):
        """Weak measurement must lose less information than projective."""
        proj_policy = ProjectiveMeasurementPolicy()
        weak_policy = WeakMeasurementPolicy(coupling_strength=0.3)
        state = _uniform_2d()
        proj_result = proj_policy.measure(state, seed=42)
        weak_result = weak_policy.measure(state, seed=42)
        self.assertLessEqual(
            weak_result.information_loss_declared,
            proj_result.information_loss_declared + 1e-10
        )

    def test_weak_measurement_deterministic(self):
        """Same seed → same weak measurement outcome."""
        policy = WeakMeasurementPolicy(coupling_strength=0.5)
        state = _uniform_2d()
        r1 = policy.measure(state, seed=7)
        r2 = policy.measure(state, seed=7)
        self.assertEqual(r1.outcome, r2.outcome)
        self.assertAlmostEqual(r1.confidence, r2.confidence, places=10)

    def test_invalid_coupling_rejected(self):
        """Coupling strength outside (0, 1] must be rejected."""
        with self.assertRaises(ValueError):
            WeakMeasurementPolicy(coupling_strength=0.0)
        with self.assertRaises(ValueError):
            WeakMeasurementPolicy(coupling_strength=1.5)


class TestCollapseEngine(unittest.TestCase):

    def _make_engine(self) -> CollapseEngine:
        engine = CollapseEngine()
        engine.register_policy(ProjectiveMeasurementPolicy())
        engine.register_policy(WeakMeasurementPolicy(0.5))
        return engine

    def test_basic_collapse_works(self):
        """A valid token+seed should produce a collapse event."""
        engine = self._make_engine()
        state = _uniform_2d()
        token = engine.issue_token("ProjectiveMeasurement", "tok-001")
        event = engine.collapse(state, token, seed=42)
        self.assertEqual(event.event_id, 0)
        self.assertEqual(event.token_id, "tok-001")
        self.assertIn(event.result.outcome, ["0", "1"])

    def test_token_single_use(self):
        """Same token cannot be used twice — must raise on second use."""
        engine = self._make_engine()
        state = _uniform_2d()
        token = engine.issue_token("ProjectiveMeasurement", "tok-002")
        engine.collapse(state, token, seed=1)
        with self.assertRaises(ValueError):
            engine.collapse(state, token, seed=2)

    def test_replay_integrity(self):
        """CollapseEngine.verify_collapse_integrity must pass after valid collapses."""
        engine = self._make_engine()
        state = _uniform_2d()
        for i in range(3):
            token = engine.issue_token("ProjectiveMeasurement", f"tok-{i}")
            engine.collapse(state, token, seed=i * 17)
        self.assertTrue(engine.verify_collapse_integrity())

    def test_total_information_loss_accumulates(self):
        """Total information loss must increase after each projective collapse."""
        engine = self._make_engine()
        state = _uniform_2d()
        for i in range(3):
            token = engine.issue_token("ProjectiveMeasurement", f"tok-acc-{i}")
            engine.collapse(state, token, seed=i)
        self.assertGreater(engine.total_information_lost, 0.0)

    def test_all_measurement_invariants_pass(self):
        """Full M1-M7 invariant suite must pass after valid operations."""
        engine = self._make_engine()
        state = _uniform_2d()
        token = engine.issue_token("ProjectiveMeasurement", "inv-tok")
        engine.collapse(state, token, seed=999)
        report = run_all_measurement_invariants(engine, ProjectiveMeasurementPolicy())
        self.assertEqual(report.failed, [], f"Invariants failed: {report.failed}")

    def test_collapse_without_token_rejected(self):
        """Passing anything other than a CollapseToken must be rejected."""
        engine = self._make_engine()
        state = _uniform_2d()
        with self.assertRaises(TypeError):
            engine.collapse(state, "fake_token", seed=0)  # type: ignore

    def test_duplicate_policy_registration_rejected(self):
        """Re-registering the same policy must raise."""
        engine = self._make_engine()
        with self.assertRaises(ValueError):
            engine.register_policy(ProjectiveMeasurementPolicy())

    def test_collapse_log_is_immutable_tuple(self):
        """collapse_log must return a tuple — not mutable."""
        engine = self._make_engine()
        state = _uniform_2d()
        tok = engine.issue_token("ProjectiveMeasurement", "mut-test")
        engine.collapse(state, tok, seed=1)
        log = engine.collapse_log
        self.assertIsInstance(log, tuple)
        with self.assertRaises((TypeError, AttributeError)):
            log[0] = None  # type: ignore


if __name__ == "__main__":
    unittest.main(verbosity=2)
