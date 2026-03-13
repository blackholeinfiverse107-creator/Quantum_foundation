"""
Cycle 3 Tests — Irreversibility, Compensation, and PointOfNoReturn
===================================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle1.state_evolution_engine import StateVector, SovereignStateEngine, Observation, identity_rule, phase_rotation_rule
from cycle2.measurement_policy import ProjectiveMeasurementPolicy
from cycle2.collapse_engine import CollapseEngine
from cycle3.timeline import CausalTimeline, CausalityViolationError, PointOfNoReturnViolationError
from cycle3.integration import QuantumFoundationSystem


def _uniform_2d() -> StateVector:
    import math
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


class TestIrreversibility(unittest.TestCase):

    def test_recorded_event_cannot_be_deleted(self):
        """Events in the timeline cannot be removed — no delete method exists."""
        timeline = CausalTimeline()
        timeline.record("TEST", payload="irreversible")
        self.assertFalse(hasattr(timeline, 'delete'))
        self.assertFalse(hasattr(timeline, 'remove'))
        self.assertFalse(hasattr(timeline, 'pop'))

    def test_recorded_event_cannot_be_modified(self):
        """CausalEvent is a frozen dataclass — cannot be mutated."""
        timeline = CausalTimeline()
        event = timeline.record("TEST", payload="data")
        with self.assertRaises((AttributeError, TypeError)):
            event.event_type = "HACKED"  # type: ignore

    def test_events_tuple_always_grows(self):
        """Timeline length must monotonically increase."""
        timeline = CausalTimeline()
        for i in range(5):
            timeline.record(f"E{i}", payload=i)
            current_len = timeline.length
            # Simulate checking: length after each add must be exactly i+1
            self.assertEqual(current_len, i + 1)


class TestCompensationOverRollback(unittest.TestCase):

    def test_compensation_adds_new_event(self):
        """Compensation must add a new event, not modify the original."""
        timeline = CausalTimeline()
        e1 = timeline.record("ORIGINAL", payload="bad_data")
        initial_len = timeline.length
        comp = timeline.compensate(e1.causal_id, "corrected_data", reason="test")
        # Compensation adds an event, not removes/replaces
        self.assertGreater(timeline.length, initial_len)
        # Original event is still there
        self.assertIn(e1.causal_id, timeline._event_index)
        self.assertTrue(comp.is_compensation)

    def test_original_event_unchanged_after_compensation(self):
        """The original event's payload must not change after compensation."""
        timeline = CausalTimeline()
        e1 = timeline.record("ORIGINAL", payload="original_payload")
        timeline.compensate(e1.causal_id, "new_payload")
        # Re-fetch the original from the index
        fetched = timeline._event_index[e1.causal_id]
        self.assertEqual(fetched.payload, "original_payload")

    def test_no_rollback_mechanism_exists(self):
        """There must be no rollback, undo, revert, or delete method."""
        timeline = CausalTimeline()
        for method in ['rollback', 'undo', 'revert', 'delete', 'remove']:
            self.assertFalse(
                hasattr(timeline, method),
                f"CausalTimeline must not have a '{method}' method (rollback is forbidden)"
            )


class TestPointOfNoReturn(unittest.TestCase):

    def test_seal_prevents_compensation_of_sealed_events(self):
        """Compensating a sealed event must raise PointOfNoReturnViolationError."""
        timeline = CausalTimeline()
        e1 = timeline.record("BEFORE_SEAL", payload=1)
        timeline.seal(e1.causal_id, reason="test seal")
        with self.assertRaises(PointOfNoReturnViolationError):
            timeline.compensate(e1.causal_id, "attempt_to_compensate")

    def test_seal_allows_new_events_after_ponr(self):
        """New events can still be added AFTER a PointOfNoReturn."""
        timeline = CausalTimeline()
        e1 = timeline.record("BEFORE_SEAL", payload=1)
        timeline.seal(e1.causal_id, reason="seal")
        # Should succeed
        e2 = timeline.record("AFTER_SEAL", payload=2)
        self.assertGreater(e2.causal_id, e1.causal_id)

    def test_ponr_cannot_go_backwards(self):
        """A PointOfNoReturn cannot seal an earlier id than already sealed."""
        timeline = CausalTimeline()
        e1 = timeline.record("A", payload=1)
        e2 = timeline.record("B", payload=2)
        timeline.seal(e2.causal_id, reason="seal B")
        with self.assertRaises(ValueError):
            timeline.seal(e1.causal_id, reason="trying to go back")

    def test_ponr_is_frozen(self):
        """PointOfNoReturn objects are frozen after creation."""
        from cycle3.causality_primitives import PointOfNoReturn
        import time
        ponr = PointOfNoReturn(sealed_at_causal_id=5, reason="test", wall_time_ns=time.time_ns())
        with self.assertRaises((AttributeError, TypeError)):
            ponr.reason = "hacked"  # type: ignore


class TestFullSystemIntegration(unittest.TestCase):

    def _make_system(self) -> QuantumFoundationSystem:
        system = QuantumFoundationSystem(_uniform_2d(), name="TestSystem")
        system.register_transition_rule("phase", phase_rotation_rule, "phase rotation")
        system.register_transition_rule("identity", identity_rule, "no-op")
        system.register_measurement_policy(ProjectiveMeasurementPolicy())
        return system

    def test_evolution_and_collapse_both_in_timeline(self):
        """State deltas and collapse events must both appear in the causal timeline."""
        system = self._make_system()
        _, ev1 = system.evolve(Observation("phase", (0.5,)))
        token = system.issue_collapse_token("ProjectiveMeasurement", "full-int-tok")
        _, ev2 = system.measure(token, seed=42)
        event_types = [e.event_type for e in system.timeline.events]
        self.assertIn("STATE_DELTA", event_types)
        self.assertIn("COLLAPSE", event_types)

    def test_timeline_ordering_holds_after_evolution_and_collapse(self):
        """Timeline must remain causally ordered after mixed operations."""
        system = self._make_system()
        system.evolve(Observation("phase", (0.3,)))
        tok = system.issue_collapse_token("ProjectiveMeasurement", "order-tok")
        system.measure(tok, seed=7)
        system.evolve(Observation("identity", ()))
        self.assertTrue(system.timeline.verify_ordering())

    def test_all_invariants_pass_in_integrated_system(self):
        """verify_all_invariants() must return no failures."""
        system = self._make_system()
        system.evolve(Observation("phase", (math.pi / 4,)))
        tok = system.issue_collapse_token("ProjectiveMeasurement", "inv-int-tok")
        system.measure(tok, seed=101)
        report = system.verify_all_invariants()
        for cycle, results in report.items():
            self.assertEqual(
                results["failed"], [],
                f"{cycle} failures: {results['failed']}"
            )

    def test_seal_and_compensate_in_integrated_system(self):
        """Seal the timeline; then compensate a future event; verify no error."""
        system = self._make_system()
        _, ev1 = system.evolve(Observation("identity", ()))
        system.seal_timeline("sealing after genesis + one evolution")
        # New evolution after seal — this CAN be compensated
        _, ev2 = system.evolve(Observation("identity", ()))
        comp = system.compensate(ev2.causal_id, "compensation_payload", "corrective event")
        self.assertTrue(comp.is_compensation)


if __name__ == "__main__":
    unittest.main(verbosity=2)
