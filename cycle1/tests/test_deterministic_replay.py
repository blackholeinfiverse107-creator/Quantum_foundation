"""
Cycle 1 Tests — Deterministic Replay
======================================

Validates core guarantee: given the same initial state and the same sequence
of observations, the engine ALWAYS produces the same final state.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import unittest
import cmath
import math

from cycle1.state_evolution_engine import (
    Observation,
    StateVector,
    SovereignStateEngine,
    phase_rotation_rule,
    dampened_amplitude_rule,
    identity_rule,
)
from cycle1.invariants import run_all_invariants


def _make_uniform_2d() -> StateVector:
    """Returns |+⟩ = (1/√2)|0⟩ + (1/√2)|1⟩"""
    amp = 1.0 / math.sqrt(2)
    return StateVector({"0": complex(amp), "1": complex(amp)})


def _make_basis_state(label: str, dim: int) -> StateVector:
    """Returns a pure basis state |label⟩ in a dim-dimensional space"""
    amps: dict = {}
    labels = [str(i) for i in range(dim)]
    for l in labels:
        amps[l] = complex(1.0) if l == label else complex(0.0)
    # Need at least the target to be non-zero
    return StateVector(amps)


class TestDeterministicReplay(unittest.TestCase):

    def _build_standard_engine(self) -> SovereignStateEngine:
        """Create a fully configured 2-qubit engine."""
        initial = _make_uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("phase_rotation", phase_rotation_rule,
                              "Apply a global phase rotation")
        engine.register_rule("dampen", dampened_amplitude_rule,
                              "Dampen a specific basis amplitude and renormalize")
        engine.register_rule("identity", identity_rule,
                              "No-op transition")
        return engine

    def test_single_step_replay(self):
        """One transition must be exactly reproducible."""
        engine = self._build_standard_engine()
        obs = Observation("phase_rotation", (math.pi / 4,))
        engine.observe(obs)

        replayed = engine.replay_from_log(
            engine.delta_log[0].prior_state,
            engine.delta_log,
        )
        self.assertEqual(replayed, engine.current_state)

    def test_multi_step_replay(self):
        """Ten sequential transitions must produce identical final state on replay."""
        engine = self._build_standard_engine()
        for i in range(10):
            obs = Observation("phase_rotation", (math.pi * i / 10,))
            engine.observe(obs)

        replayed = engine.replay_from_log(
            engine.delta_log[0].prior_state,
            engine.delta_log,
        )
        self.assertEqual(replayed, engine.current_state)

    def test_identity_replay(self):
        """Identity rule: state unchanged, replay still consistent."""
        engine = self._build_standard_engine()
        engine.observe(Observation("identity", ()))
        engine.observe(Observation("identity", ()))
        result = engine.verify_replay_integrity()
        self.assertTrue(result)

    def test_mixed_rule_replay(self):
        """Mix of different rule types must replay deterministically."""
        engine = self._build_standard_engine()
        engine.observe(Observation("phase_rotation", (0.5,)))
        engine.observe(Observation("dampen", ("1", 0.8)))
        engine.observe(Observation("phase_rotation", (1.0,)))

        replayed = engine.replay_from_log(
            engine.delta_log[0].prior_state,
            engine.delta_log,
        )
        self.assertEqual(replayed, engine.current_state)

    def test_replay_is_independent(self):
        """Replay must not mutate the original engine state."""
        engine = self._build_standard_engine()
        engine.observe(Observation("phase_rotation", (math.pi,)))
        original_state = engine.current_state
        original_log_len = len(engine.delta_log)

        # Run replay — should not touch the original engine
        engine.replay_from_log(engine.delta_log[0].prior_state, engine.delta_log)

        self.assertEqual(engine.current_state, original_state)
        self.assertEqual(len(engine.delta_log), original_log_len)

    def test_empty_log_replay(self):
        """Engine with no observations replays trivially to initial state."""
        initial = _make_uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("identity", identity_rule)
        result = engine.verify_replay_integrity()
        self.assertTrue(result)

    def test_all_invariants_pass_after_evolution(self):
        """All invariants must hold after a sequence of valid transitions."""
        engine = self._build_standard_engine()
        for i in range(5):
            engine.observe(Observation("phase_rotation", (math.pi * i / 5.0,)))

        report = run_all_invariants(engine)
        self.assertEqual(
            report.failed, [],
            f"Invariants failed: {report.failed}"
        )
        self.assertGreater(len(report.passed), 0)


class TestStateDeltaProperties(unittest.TestCase):

    def test_delta_has_correct_sequence_numbers(self):
        """Sequence numbers must be 0, 1, 2, …"""
        initial = _make_uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("identity", identity_rule)

        for expected_seq in range(5):
            delta = engine.observe(Observation("identity", ()))
            self.assertEqual(delta.sequence_number, expected_seq)

    def test_delta_prior_and_next_differ_after_phase(self):
        """A phase rotation must produce a genuinely different next state."""
        initial = _make_uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("phase_rotation", phase_rotation_rule)

        delta = engine.observe(Observation("phase_rotation", (math.pi / 3,)))
        self.assertNotEqual(delta.prior_state, delta.next_state)

    def test_delta_is_frozen(self):
        """StateDelta objects must be immutable (frozen dataclass)."""
        initial = _make_uniform_2d()
        engine = SovereignStateEngine(initial)
        engine.register_rule("identity", identity_rule)
        delta = engine.observe(Observation("identity", ()))

        with self.assertRaises((AttributeError, TypeError)):
            delta.sequence_number = 999  # type: ignore


if __name__ == "__main__":
    unittest.main(verbosity=2)
