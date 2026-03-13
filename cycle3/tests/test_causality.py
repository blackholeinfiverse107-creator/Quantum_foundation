"""
Cycle 3 Tests — Causality Ordering & Irreversibility Enforcement
================================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import math
import unittest

from cycle3.causality_primitives import CausalEvent, CausalLink, LogicalClock, PointOfNoReturn
from cycle3.timeline import CausalTimeline, CausalityViolationError, PointOfNoReturnViolationError


class TestLogicalClock(unittest.TestCase):

    def test_clock_starts_at_zero(self):
        clk = LogicalClock()
        self.assertEqual(clk.peek(), 0)

    def test_tick_increments_by_one(self):
        clk = LogicalClock()
        for i in range(1, 6):
            val = clk.tick()
            self.assertEqual(val, i)

    def test_clock_never_decreases(self):
        clk = LogicalClock()
        for _ in range(10):
            clk.tick()
        val = clk.peek()
        for _ in range(5):
            clk.tick()
        self.assertGreater(clk.peek(), val)

    def test_negative_start_rejected(self):
        with self.assertRaises(ValueError):
            LogicalClock(start=-1)


class TestCausalEventOrdering(unittest.TestCase):

    def test_predecessor_must_precede(self):
        """predecessor_id must be strictly less than causal_id."""
        with self.assertRaises(ValueError):
            CausalEvent(
                causal_id=3, event_type="TEST", payload=None,
                predecessor_id=3, wall_time_ns=0  # same id — invalid
            )

    def test_valid_event_created(self):
        event = CausalEvent(
            causal_id=5, event_type="TEST", payload="data",
            predecessor_id=4, wall_time_ns=0
        )
        self.assertEqual(event.causal_id, 5)
        self.assertEqual(event.predecessor_id, 4)

    def test_genesis_event_has_no_predecessor(self):
        genesis = CausalEvent(
            causal_id=1, event_type="GENESIS", payload=None,
            predecessor_id=None, wall_time_ns=0
        )
        self.assertIsNone(genesis.predecessor_id)


class TestCausalLink(unittest.TestCase):

    def test_cause_must_precede_effect(self):
        """cause_id must be < effect_id."""
        with self.assertRaises(ValueError):
            CausalLink(cause_id=5, effect_id=5)

    def test_valid_link_created(self):
        link = CausalLink(cause_id=1, effect_id=2, mechanism="OBSERVATION")
        self.assertEqual(link.cause_id, 1)


class TestCausalTimelineOrdering(unittest.TestCase):

    def test_events_are_strictly_ordered(self):
        timeline = CausalTimeline()
        e1 = timeline.record("A", payload="first")
        e2 = timeline.record("B", payload="second")
        e3 = timeline.record("C", payload="third")
        self.assertLess(e1.causal_id, e2.causal_id)
        self.assertLess(e2.causal_id, e3.causal_id)

    def test_verify_ordering_passes(self):
        timeline = CausalTimeline()
        for i in range(5):
            timeline.record(f"EVENT_{i}", payload=i)
        self.assertTrue(timeline.verify_ordering())

    def test_events_tuple_is_immutable(self):
        timeline = CausalTimeline()
        timeline.record("X", payload=None)
        events = timeline.events
        self.assertIsInstance(events, tuple)
        with self.assertRaises((TypeError, AttributeError)):
            events[0] = None  # type: ignore

    def test_event_index_is_consistent(self):
        timeline = CausalTimeline()
        e = timeline.record("Y", payload="data")
        self.assertIn(e.causal_id, timeline._event_index)

    def test_causal_chain_retrieval(self):
        timeline = CausalTimeline()
        e1 = timeline.record("A", payload=1)
        e2 = timeline.record("B", payload=2)
        e3 = timeline.record("C", payload=3)
        chain = timeline.get_chain(e3.causal_id)
        ids = [e.causal_id for e in chain]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(ids[-1], e3.causal_id)

    def test_chain_for_nonexistent_event_raises(self):
        timeline = CausalTimeline()
        with self.assertRaises(CausalityViolationError):
            timeline.get_chain(999)


if __name__ == "__main__":
    unittest.main(verbosity=2)
